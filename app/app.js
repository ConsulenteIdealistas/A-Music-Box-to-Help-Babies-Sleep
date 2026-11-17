"use strict";
/*
 * A Music Box to Help Babies Sleep — PWA
 * 3層（オルゴール / 心音 / さざ波=血流ベッド）を Web Audio API で
 * リアルタイム合成する。音響パラメータは 2026-11-17 に確定した
 * 設計（audio/render_mix.py のオフライン版と同一）に揃えてある。
 *
 * 基本設計思想（DESIGN.md）: 同じ入力には同じ出力（決定性）、
 * パラメータは独立・協調制御、変化はイージングで滑らかに、
 * 確率的な揺らぎは入れない、制御は事前定義した数理モデルのみ。
 * 状態と遷移はプリセットとして JSON で保存する（正本は
 * app/presets.json、ユーザーの保存分は localStorage に同形式）。
 *
 * 確定設計の要点:
 *   統合伝達曲線 … 250 Hz の1極ローパス（250 Hz 以下は平坦、
 *     それ以上 −6 dB/oct）。根拠は Gerhardt 1990 の実測
 *     （audio/bed_integration_2026-11-17.md）。音楽層と血流層の
 *     両方に同じ曲線を通す。Web Audio の BiquadFilter は2極
 *     （−12 dB/oct）なので、1極は係数を直接計算して
 *     IIRFilterNode / オフライン処理で実現する。
 *   心音 … 55 Hz サインの lub-dub（間隔 280 ms、減衰 exp(−22t)）。
 *     BPM は可変（既定 70 = 母体安静時心拍 60–80 の中央）。
 *   血流 … 白色ノイズ → 統合曲線 → 心拍同期の surge
 *     （0.55 + 0.45·exp(−4·phase)、25 ms で平滑化。オフライン版で
 *     拍ごとの 0.44 のゲイン段差を測定し除去した形）→
 *     0.05 Hz の swell（±10%）。
 *   バランス … スライダ既定位置でオフライン完成ミックスの実測
 *     比になるよう、各層に設計ゲインを置いた。心音/音楽 −16.7 dB、
 *     血流/音楽 −26.2 dB（4曲の発音中バランス中央値 −16.3 dB と
 *     オフライン stem 実測 0.01311 / 0.00439 から導出、
 *     analysis/four_songs_measurements.csv）。
 *
 * TODO: 最大音量リミッター値の確定（安全側統計から）、
 *   エントレインメント減速カーブ（BPM 85 → 65）、画面ロック。
 *
 * オルゴール音源: audio/render_klank.py で書き出し、audio/make_loop.py で
 * ループ化した WAV を app/assets/ に置く（生成物なのでリポジトリには
 * 含めない）。読み込み時に統合曲線でフィルタした複製を作り、
 * RMS を揃えてからループ再生する。
 */

const SONGS = [
  { id: "brahms", label: "ブラームスの子守歌", file: "assets/brahms_wiegenlied_klank_loop.wav" },
  { id: "yurikago", label: "ゆりかごのうた", file: "assets/yurikago_no_uta_klank_loop.wav" },
  { id: "moldau", label: "モルダウ主題", file: "assets/moldau_theme_klank_loop.wav" },
  { id: "vissi", label: "歌に生き、愛に生き", file: "assets/vissi_darte_klank_loop.wav" },
];

// --- 確定設計の定数（出所は冒頭コメント） ---
const KNEE_HZ = 250;            // 統合伝達曲線の折れ点
const HEART_FREQ_HZ = 55;       // 心音のサイン周波数
const LUB_DUB_S = 0.28;         // lub-dub 間隔
const HEART_DECAY = 22.0;       // 心音エンベロープ exp(-22t)
const SURGE_BASE = 0.55, SURGE_DEPTH = 0.45, SURGE_RATE = 4.0;
const SURGE_SMOOTH_S = 0.025;   // surge の平滑化（25 ms）
const SWELL_HZ = 0.05, SWELL_DEPTH = 0.10;
const MUSIC_NORM_RMS = 0.10;    // 音楽層の正規化 RMS
const DESIGN_GAIN_HEART = 0.111; // 心音の設計ゲイン（導出は冒頭）
const DESIGN_GAIN_FLOW = 0.095;  // 血流の設計ゲイン（同上）
const MASTER_LEVEL = 0.9;       // TODO: リミッター確定まで従来値
const FADE_OUT_S = 30;          // タイマー終了前のフェード長
const SEED = 20261115;          // 決定性のためノイズも種固定（オフライン版と同値）
const VOLUME_EASE_S = 0.05;     // スライダ変更のイージング時定数

// 種固定 PRNG（mulberry32）: 開くたびに同じノイズ波形にする
function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

let ctx = null;
let master, gainMusic, gainHeart, gainWaves, surgeNode, heartDesign, flowDesign;
let heartTimer = null, fadeTimer = null, wavesNodes = null;
let thenTimer = null; // プリセットの then（継続状態）の予約。新しい操作で取り消す
let musicSrc = null, musicSrcGain = null, musicStartedAt = 0, musicOffset = 0;
let musicCrossfadeGen = 0; // クロスフェードの世代（古い非同期処理の割り込みを防ぐ）
const musicBuffers = {}; // "id@cutoff" -> AudioBuffer（フィルタ済み・正規化済み）
let playing = false;
let playGen = 0; // 再生世代（停止直後の再開で suspend が競合しないよう）
let bpmCurrent = 70;            // 心音 BPM の現在値（遷移で連続的に変わる）
let lowpassHz = KNEE_HZ;        // ローパスの現在値（プリセットで変更可）

const $ = (id) => document.getElementById(id);

// --- イージング関数（DESIGN.md §4: 初期標準 Ease In Out、比較基準 Linear、
// パラメータごとに異なる曲線を使ってよい） ---
const EASING = {
  linear: (t) => t,
  easeIn: (t) => t * t * t,
  easeOut: (t) => 1 - Math.pow(1 - t, 3),
  easeInOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  smoothstep: (t) => t * t * (3 - 2 * t),
};
function easingSamples(name, points = 64) {
  const f = EASING[name] || EASING.easeInOut;
  const c = new Float32Array(points);
  for (let i = 0; i < points; i++) c[i] = f(i / (points - 1));
  return c;
}

// --- 遷移エンジン（DESIGN.md §2 の Easing Engine） ---
// key ごとに1本の遷移を持ち、同じ key の再登録で置き換える。
const tweens = new Map();
let tweenTimer = null;
function addTween(key, durS, curveName, apply, done) {
  if (!(durS > 0)) { apply(1); if (done) done(); return; }
  tweens.set(key, {
    t0: performance.now(), dur: durS * 1000,
    ease: EASING[curveName] || EASING.easeInOut, apply, done,
  });
  if (!tweenTimer) tweenTimer = setInterval(tickTweens, 50);
}
function tickTweens() {
  const now = performance.now();
  for (const [key, tw] of tweens) {
    const p = Math.min(1, (now - tw.t0) / tw.dur);
    tw.apply(tw.ease(p));
    if (p >= 1) { tweens.delete(key); if (tw.done) tw.done(); }
  }
  if (!tweens.size) { clearInterval(tweenTimer); tweenTimer = null; }
}
function cancelTween(key) { tweens.delete(key); }

// 1極ローパスの係数（render_mix.py の one_pole_alpha と同一式）
function onePoleAlpha(cutoffHz, sampleRate) {
  return 1.0 - Math.exp(-2.0 * Math.PI * cutoffHz / sampleRate);
}

// Float32Array に1極ローパスをかける（wrap=true で末尾→先頭を
// つないで2周し、2周目を返す: ループ境界でフィルタ状態が連続する）
function lowpassBuffer(data, alpha, wrap) {
  const out = new Float32Array(data.length);
  let y = 0;
  const passes = wrap ? 2 : 1;
  for (let p = 0; p < passes; p++) {
    for (let i = 0; i < data.length; i++) {
      y += alpha * (data[i] - y);
      if (p === passes - 1) out[i] = y;
    }
  }
  return out;
}

// surge カーブ（1周期分、25 ms 平滑化済み・周期境界も連続）
function surgeCurve(points = 128) {
  const raw = new Float32Array(points);
  for (let i = 0; i < points; i++) {
    raw[i] = SURGE_BASE + SURGE_DEPTH * Math.exp(-SURGE_RATE * (i / points));
  }
  // 周期信号として平滑化（2周期つないで2周期目を取る）
  const period = 60 / bpmCurrent;
  const a = 1.0 - Math.exp(-1.0 / (SURGE_SMOOTH_S * (points / period)));
  const out = new Float32Array(points);
  let y = raw[points - 1];
  for (let p = 0; p < 2; p++) {
    for (let i = 0; i < points; i++) {
      y += a * (raw[i] - y);
      if (p === 1) out[i] = y;
    }
  }
  return out;
}

function buildGraph() {
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  master = ctx.createGain();
  master.gain.value = MASTER_LEVEL;
  master.connect(ctx.destination);

  gainMusic = ctx.createGain();
  gainMusic.connect(master);

  heartDesign = ctx.createGain();
  heartDesign.gain.value = DESIGN_GAIN_HEART;
  gainHeart = ctx.createGain();
  heartDesign.connect(gainHeart).connect(master);

  // 血流: ノイズ → 統合曲線(IIR 1極) → surge → swell → 設計ゲイン
  surgeNode = ctx.createGain();
  surgeNode.gain.value = SURGE_BASE + SURGE_DEPTH;
  const swellNode = ctx.createGain();
  swellNode.gain.value = 1.0;
  const lfo = ctx.createOscillator();
  lfo.frequency.value = SWELL_HZ;
  const lfoGain = ctx.createGain();
  lfoGain.gain.value = SWELL_DEPTH;
  lfo.connect(lfoGain).connect(swellNode.gain);
  lfo.start();
  flowDesign = ctx.createGain();
  flowDesign.gain.value = DESIGN_GAIN_FLOW;
  gainWaves = ctx.createGain();
  surgeNode.connect(swellNode).connect(flowDesign).connect(gainWaves).connect(master);
  wavesNodes = { swellNode, lfo };
  applyVolumes();
}

// --- 心音: 55 Hz サインの lub-dub（オフライン版と同一波形） ---
function thump(when, peak) {
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = "sine";
  osc.frequency.value = HEART_FREQ_HZ;
  g.gain.setValueAtTime(peak, when);
  g.gain.setTargetAtTime(0, when, 1.0 / HEART_DECAY);
  osc.connect(g).connect(heartDesign);
  osc.start(when);
  osc.stop(when + 0.3);
}
function scheduleHeart() {
  clearTimeout(heartTimer);
  if (!playing) return;
  const period = 60 / bpmCurrent;
  const t = ctx.currentTime + 0.05;
  thump(t, 1.0);                 // lub
  thump(t + LUB_DUB_S, 0.55);    // dub（280 ms 固定）
  // 血流の surge を同じ拍に同期させる
  if (surgeNode) {
    const curve = surgeCurve();
    surgeNode.gain.cancelScheduledValues(t);
    surgeNode.gain.setValueCurveAtTime(curve, t, period);
  }
  heartTimer = setTimeout(scheduleHeart, period * 1000);
}

// --- さざ波（血流）: 白色ノイズを統合曲線で整形してループ ---
function shapedNoiseBuffer(cutoff) {
  const len = ctx.sampleRate * 8;
  const buf = ctx.createBuffer(1, len, ctx.sampleRate);
  const white = new Float32Array(len);
  const rng = mulberry32(SEED);
  for (let i = 0; i < len; i++) white[i] = rng() * 2 - 1;
  const shaped = lowpassBuffer(white, onePoleAlpha(cutoff, ctx.sampleRate), true);
  // ループ境界の波形段差を 50 ms クロスフェードで消す
  const xf = Math.floor(ctx.sampleRate * 0.05);
  for (let i = 0; i < xf; i++) {
    const k = i / xf;
    shaped[i] = shaped[i] * k + shaped[len - xf + i] * (1 - k);
  }
  buf.getChannelData(0).set(shaped);
  return buf;
}
function spawnWaves(cutoff, gainVal) {
  const src = ctx.createBufferSource();
  src.buffer = shapedNoiseBuffer(cutoff);
  src.loop = true;
  const g = ctx.createGain();
  g.gain.value = gainVal;
  src.connect(g).connect(surgeNode);
  src.start();
  return { src, g };
}
function startWaves() {
  const w = spawnWaves(lowpassHz, 1);
  wavesNodes.src = w.src;
  wavesNodes.srcGain = w.g;
}
function stopWaves() {
  if (wavesNodes && wavesNodes.src) {
    try { wavesNodes.src.stop(); } catch (_) {}
    wavesNodes.src = null;
    wavesNodes.srcGain = null;
  }
}
// ローパス変更: 新しい整形で作り直した音源とクロスフェードする
function crossfadeWavesTo(cutoff, durS, curveName) {
  if (!wavesNodes || !wavesNodes.src) return;
  const old = { src: wavesNodes.src, g: wavesNodes.srcGain };
  const nw = spawnWaves(cutoff, 0);
  const t = ctx.currentTime;
  const inC = easingSamples(curveName);
  const outC = new Float32Array(inC.length);
  for (let i = 0; i < inC.length; i++) outC[i] = 1 - inC[i];
  nw.g.gain.setValueCurveAtTime(inC, t, durS);
  old.g.gain.setValueCurveAtTime(outC, t, durS);
  wavesNodes.src = nw.src;
  wavesNodes.srcGain = nw.g;
  setTimeout(() => { try { old.src.stop(); } catch (_) {} old.g.disconnect(); }, (durS + 0.2) * 1000);
}

// --- オルゴール: 読み込み時に統合曲線を適用し RMS を正規化 ---
async function loadSong(id, cutoff = lowpassHz) {
  const key = id + "@" + cutoff;
  if (musicBuffers[key]) return musicBuffers[key];
  const song = SONGS.find((s) => s.id === id);
  const res = await fetch(song.file);
  if (!res.ok) throw new Error("fetch failed: " + song.file);
  const raw = await ctx.decodeAudioData(await res.arrayBuffer());
  const src = raw.getChannelData(0);
  const filtered = lowpassBuffer(src, onePoleAlpha(cutoff, ctx.sampleRate), true);
  let sum = 0;
  for (let i = 0; i < filtered.length; i++) sum += filtered[i] * filtered[i];
  const rms = Math.sqrt(sum / filtered.length);
  const norm = MUSIC_NORM_RMS / Math.max(rms, 1e-6);
  const buf = ctx.createBuffer(1, filtered.length, ctx.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < filtered.length; i++) d[i] = filtered[i] * norm;
  musicBuffers[key] = buf;
  return buf;
}
function spawnMusic(buf, offset, gainVal) {
  const src = ctx.createBufferSource();
  src.buffer = buf;
  src.loop = true;
  const g = ctx.createGain();
  g.gain.value = gainVal;
  src.connect(g).connect(gainMusic);
  src.start(0, offset % buf.duration);
  return { src, g };
}
async function startMusic() {
  const id = $("song").value;
  try {
    const buf = await loadSong(id, lowpassHz);
    stopMusic();
    const m = spawnMusic(buf, 0, 1);
    musicSrc = m.src;
    musicSrcGain = m.g;
    musicStartedAt = ctx.currentTime;
    musicOffset = 0;
    $("songStatus").textContent = "";
  } catch (e) {
    // 音源ファイルが無い場合は他の層だけで再生を続ける
    $("songStatus").textContent = "オルゴール音源が見つかりません（app/assets/ にループ WAV を配置してください）";
  }
}
function stopMusic() {
  if (!musicSrc) return;
  try { musicSrc.stop(); } catch (_) {}
  musicSrc.disconnect();
  if (musicSrcGain) musicSrcGain.disconnect();
  musicSrc = null;
  musicSrcGain = null;
}
function musicPos() {
  if (!musicSrc) return 0;
  return (musicOffset + (ctx.currentTime - musicStartedAt)) % musicSrc.buffer.duration;
}
// ローパス変更: 同じ再生位置から新しいフィルタ版をクロスフェードで差し替える
async function crossfadeMusicTo(cutoff, durS, curveName) {
  if (!musicSrc) return;
  const gen = ++musicCrossfadeGen;
  try {
    const buf = await loadSong($("song").value, cutoff);
    // 読み込みを待つ間に新しいクロスフェードが始まっていたら、
    // そちらの状態（musicSrc 等）を壊さないよう何もしない
    if (gen !== musicCrossfadeGen) return;
    const pos = musicPos();
    const old = { src: musicSrc, g: musicSrcGain };
    const nw = spawnMusic(buf, pos, 0);
    const t = ctx.currentTime;
    const inC = easingSamples(curveName);
    const outC = new Float32Array(inC.length);
    for (let i = 0; i < inC.length; i++) outC[i] = 1 - inC[i];
    nw.g.gain.setValueCurveAtTime(inC, t, durS);
    if (old.g) old.g.gain.setValueCurveAtTime(outC, t, durS);
    musicSrc = nw.src;
    musicSrcGain = nw.g;
    musicStartedAt = t;
    musicOffset = pos;
    setTimeout(() => { try { old.src.stop(); } catch (_) {} if (old.g) old.g.disconnect(); }, (durS + 0.2) * 1000);
  } catch (e) { /* 音源が無い場合は現状維持 */ }
}

function applyVolumes() {
  if (!ctx) return;
  // スライダ変更もイージングで滑らかに（基本設計思想 3）
  const t = ctx.currentTime;
  gainMusic.gain.setTargetAtTime($("volMusic").value / 100, t, VOLUME_EASE_S);
  gainHeart.gain.setTargetAtTime($("volHeart").value / 100, t, VOLUME_EASE_S);
  gainWaves.gain.setTargetAtTime($("volWaves").value / 100, t, VOLUME_EASE_S);
}

// フェードアウト曲線（Smoothstep: 滑らかな開始・終了、DESIGN.md §4）
function fadeCurve(points = 32) {
  const c = new Float32Array(points);
  for (let i = 0; i < points; i++) {
    c[i] = 1 - EASING.smoothstep(i / (points - 1));
  }
  return c;
}

function startFadeOut(minutes) {
  clearTimeout(fadeTimer);
  if (!minutes) return;
  fadeTimer = setTimeout(() => {
    if (!ctx || !playing) return;
    const t = ctx.currentTime;
    const curve = fadeCurve();
    const scaled = new Float32Array(curve.length);
    for (let i = 0; i < curve.length; i++) scaled[i] = curve[i] * master.gain.value;
    master.gain.cancelScheduledValues(t);
    master.gain.setValueCurveAtTime(scaled, t, FADE_OUT_S);
    setTimeout(stop, (FADE_OUT_S + 1) * 1000);
  }, (minutes * 60 - FADE_OUT_S) * 1000);
}

async function play() {
  if (!ctx) {
    try { buildGraph(); }
    catch (_) {
      // AudioContext を作れない環境では黙って無反応にならず知らせる
      $("songStatus").textContent = "音声を開始できませんでした";
      return;
    }
  }
  await ctx.resume();
  playing = true;
  playGen++;
  const t = ctx.currentTime;
  master.gain.cancelScheduledValues(t);
  master.gain.setValueAtTime(0, t);
  master.gain.linearRampToValueAtTime(MASTER_LEVEL, t + 1.0); // 1秒フェードイン
  scheduleHeart();
  startWaves();
  startMusic();
  startFadeOut(Number($("timer").value));
  $("playBtn").textContent = "■ 停止";
}
function stop() {
  // 予約済みの then は再生状態によらず取り消す（停止後に状態が変わらないように）
  clearTimeout(thenTimer);
  thenTimer = null;
  if (!playing) return;
  playing = false;
  clearTimeout(heartTimer);
  clearTimeout(fadeTimer);
  // 音源はフェードが終わってから止める（鳴っている途中で切らない）
  const musicToStop = musicSrc;
  musicSrc = null;
  const wavesToStop = wavesNodes && wavesNodes.src;
  if (wavesNodes) wavesNodes.src = null;
  if (ctx && ctx.state === "running") {
    const t = ctx.currentTime;
    master.gain.cancelScheduledValues(t);
    master.gain.setTargetAtTime(0, t, 0.2); // 0.8 秒ほどで消える
    const c = ctx;
    const gen = playGen;
    setTimeout(() => {
      if (musicToStop) { try { musicToStop.stop(); } catch (_) {} }
      if (wavesToStop) { try { wavesToStop.stop(); } catch (_) {} }
      if (playGen === gen && !playing) c.suspend();
    }, 900);
  }
  $("playBtn").textContent = "▶ 再生";
}

// --- プリセット（状態＋遷移を JSON で保存する、DESIGN.md 参照） ---
// 正本プリセットは app/presets.json。ユーザーが保存したプリセットは
// localStorage に同じ形式で入る。JSON ファイルへの書き出しと、
// 書き出したファイルの読み込み（形式を検証してから取り込む）ができる。
// parameters で省略した項目は変更しない。then は遷移完了後に続けて
// 適用する次の状態（エントレインメント減速用）。
let builtinPresets = [], userPresets = [];
function curveFor(preset, param) {
  const t = preset.transition || {};
  const per = (t.parameters || {})[param] || {};
  return per.curve || t.curve || "easeInOut";
}
function applyPreset(preset) {
  // 前のプリセットが予約した then は取り消す（後から来た操作が優先）
  clearTimeout(thenTimer);
  thenTimer = null;
  const P = preset.parameters || {};
  const dur = playing ? Number((preset.transition || {}).duration || 0) : 0;
  if (P.gain) {
    for (const [layer, el] of [["music", "volMusic"], ["heart", "volHeart"], ["waves", "volWaves"]]) {
      if (P.gain[layer] == null) continue;
      const from = Number($(el).value), target = Number(P.gain[layer]);
      addTween("gain." + layer, dur, curveFor(preset, "gain"), (e) => {
        $(el).value = Math.round(from + (target - from) * e);
        applyVolumes();
      });
    }
  }
  if (P.bpm != null) {
    const from = bpmCurrent, target = Number(P.bpm);
    addTween("bpm", dur, (preset.transition || {}).curve || "easeInOut", (e) => {
      bpmCurrent = from + (target - from) * e;
      $("bpm").value = Math.round(bpmCurrent);
      $("bpmVal").textContent = Math.round(bpmCurrent);
    });
  }
  if (P.lowpassHz != null && Number(P.lowpassHz) !== lowpassHz) {
    const target = Number(P.lowpassHz);
    lowpassHz = target;
    $("lpVal").textContent = target;
    if (playing && ctx) {
      const d = Math.max(dur, 0.3);
      crossfadeMusicTo(target, d, curveFor(preset, "lowpass"));
      crossfadeWavesTo(target, d, curveFor(preset, "lowpass"));
    }
  }
  if (preset.then) {
    const next = preset.then;
    thenTimer = setTimeout(() => { thenTimer = null; applyPreset(next); }, (dur + 0.3) * 1000);
  }
}
function loadUserPresets() {
  const raw = localStorage.getItem("lullaby.presets");
  if (raw == null) { userPresets = []; return; }
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) throw new Error("not an array");
    userPresets = parsed;
  } catch (_) {
    // 壊れた保存分は黙って捨てず、生の文字列を退避キーに残してから
    // 初期化する（復旧や原因調査の手がかりを失わないため）
    try { localStorage.setItem("lullaby.presets.corrupt", raw); } catch (_) {}
    userPresets = [];
  }
}
// 保存できたら true、容量超過などで書けなかったら false を返す
function storeUserPresets() {
  try { localStorage.setItem("lullaby.presets", JSON.stringify(userPresets)); return true; }
  catch (_) { return false; }
}
function refreshPresetOptions() {
  const sel = $("preset");
  sel.innerHTML = "";
  const ph = document.createElement("option");
  ph.value = "";
  ph.textContent = "プリセットを選ぶ";
  sel.appendChild(ph);
  const mk = (label, list, prefix) => {
    if (!list.length) return;
    const g = document.createElement("optgroup");
    g.label = label;
    list.forEach((p, i) => {
      const o = document.createElement("option");
      o.value = prefix + i;
      o.textContent = p.name || "(無名)";
      g.appendChild(o);
    });
    sel.appendChild(g);
  };
  mk("標準プリセット", builtinPresets, "b:");
  mk("保存したプリセット", userPresets, "u:");
  $("deletePreset").disabled = true;
}
function selectedPreset() {
  const v = $("preset").value;
  if (!v) return null;
  const parts = v.split(":");
  const list = parts[0] === "b" ? builtinPresets : userPresets;
  return { preset: list[Number(parts[1])], isUser: parts[0] === "u", index: Number(parts[1]) };
}
async function initPresets() {
  loadUserPresets();
  try {
    const res = await fetch("presets.json");
    if (!res.ok) throw new Error("fetch failed: presets.json");
    // 正本も読み込み時と同じ検証を通してから使う（壊れた正本で
    // 状態系が壊れないように。不正なら標準プリセットなしとして扱う）
    const r = validatePresetData(await res.json());
    if (r.ok) {
      builtinPresets = r.presets;
    } else {
      console.warn("presets.json の形式が不正なため標準プリセットを使いません:", r.error);
      $("importStatus").textContent = "標準プリセットを読み込めませんでした";
    }
  } catch (_) {
    // 読み込み自体に失敗したら、黙って空にせず利用者に知らせる
    $("importStatus").textContent = "標準プリセットを読み込めませんでした";
  }
  refreshPresetOptions();
}
function currentParams() {
  return {
    bpm: Math.round(bpmCurrent),
    gain: {
      music: Number($("volMusic").value),
      heart: Number($("volHeart").value),
      waves: Number($("volWaves").value),
    },
    lowpassHz,
  };
}

// --- プリセット読み込み（インポート）の検証 ---
// 受け付けるのは、書き出し形式（{version, presets}、正本 presets.json
// と同形式）と、プリセット単体のオブジェクト。1件でも形式が違う
// ものがあれば全体を拒否し、何も取り込まない（部分的な取り込みで
// 保存分が中途半端な状態になるのを避ける）。
const PRESET_CURVES = ["linear", "easeIn", "easeOut", "easeInOut", "smoothstep"];
const PRESET_PARAM_KEYS = ["bpm", "gain", "lowpassHz", "reverb"];
const PRESET_GAIN_LAYERS = ["music", "heart", "waves"];

function isPlainObject(v) {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}
function isFiniteNumber(v) {
  return typeof v === "number" && Number.isFinite(v);
}
// transition の検証。問題があれば日本語の理由を、なければ null を返す。
function presetTransitionError(tr, where) {
  if (!isPlainObject(tr)) return where + " の transition がオブジェクトではありません";
  if (!isFiniteNumber(tr.duration)) return where + " の transition.duration が数値ではありません";
  if (tr.curve != null && !PRESET_CURVES.includes(tr.curve)) {
    return where + " の transition.curve \"" + tr.curve + "\" は使えません（使えるのは " + PRESET_CURVES.join(" / ") + "）";
  }
  if (tr.parameters != null) {
    if (!isPlainObject(tr.parameters)) return where + " の transition.parameters がオブジェクトではありません";
    for (const [k, v] of Object.entries(tr.parameters)) {
      if (v == null) continue;
      if (!isPlainObject(v)) return where + " の transition.parameters." + k + " がオブジェクトではありません";
      if (v.curve != null && !PRESET_CURVES.includes(v.curve)) {
        return where + " の transition.parameters." + k + ".curve \"" + v.curve + "\" は使えません";
      }
    }
  }
  return null;
}
// 状態（parameters / transition / then）の検証。then は名前なしで再帰する。
function presetStateError(p, where) {
  if (!isPlainObject(p.parameters)) return where + " に parameters がありません";
  for (const k of Object.keys(p.parameters)) {
    if (!PRESET_PARAM_KEYS.includes(k)) return where + " に不明なパラメータ \"" + k + "\" があります";
  }
  const P = p.parameters;
  if (P.bpm != null && !isFiniteNumber(P.bpm)) return where + " の parameters.bpm が数値ではありません";
  if (P.lowpassHz != null && !(isFiniteNumber(P.lowpassHz) && P.lowpassHz > 0)) {
    return where + " の parameters.lowpassHz が正の数値ではありません";
  }
  if (P.gain != null) {
    if (!isPlainObject(P.gain)) return where + " の parameters.gain がオブジェクトではありません";
    for (const [k, v] of Object.entries(P.gain)) {
      if (!PRESET_GAIN_LAYERS.includes(k)) return where + " の parameters.gain に不明な層 \"" + k + "\" があります";
      if (!isFiniteNumber(v)) return where + " の parameters.gain." + k + " が数値ではありません";
    }
  }
  if (P.reverb != null && !isPlainObject(P.reverb)) return where + " の parameters.reverb がオブジェクトではありません";
  if (p.transition != null) {
    const e = presetTransitionError(p.transition, where);
    if (e) return e;
  }
  if (p.then != null) {
    if (!isPlainObject(p.then)) return where + " の then がオブジェクトではありません";
    const e = presetStateError(p.then, where + " の then");
    if (e) return e;
  }
  return null;
}
// パース済みデータ全体の検証。{ ok: true, presets } か { ok: false, error } を返す。
function validatePresetData(data) {
  let list;
  if (isPlainObject(data) && Array.isArray(data.presets)) list = data.presets;
  else if (isPlainObject(data) && ("name" in data || "parameters" in data)) list = [data];
  else return { ok: false, error: "プリセットの形式ではありません（presets の配列、またはプリセット単体のオブジェクトが必要です）" };
  if (!list.length) return { ok: false, error: "プリセットが1件も含まれていません" };
  for (let i = 0; i < list.length; i++) {
    const p = list[i];
    if (!isPlainObject(p)) return { ok: false, error: "プリセット " + (i + 1) + " 件目がオブジェクトではありません" };
    if (typeof p.name !== "string" || !p.name.trim()) {
      return { ok: false, error: "プリセット " + (i + 1) + " 件目に名前（name）がありません" };
    }
    const e = presetStateError(p, "プリセット「" + p.name + "」");
    if (e) return { ok: false, error: e };
  }
  return { ok: true, presets: list };
}
// ファイルの中身（テキスト）から検証までをまとめた純粋関数。
function parsePresetImport(text) {
  let data;
  try { data = JSON.parse(text); }
  catch (_) { return { ok: false, error: "JSON として解釈できないファイルです" }; }
  return validatePresetData(data);
}
// 重複判定用の安定した JSON 化（オブジェクトのキー順に依存しない）。
function stableStringify(v) {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) {
    return "[" + v.map((x) => (x === undefined ? "null" : stableStringify(x))).join(",") + "]";
  }
  const keys = Object.keys(v).filter((k) => v[k] !== undefined).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + stableStringify(v[k])).join(",") + "}";
}
// プリセットの同一性を決める署名（名前と、状態・遷移・続きの内容）。
function presetSignature(p) {
  return stableStringify({
    name: p.name, parameters: p.parameters, transition: p.transition, then: p.then,
  });
}
// 取り込み候補を、既存の保存プリセットと候補同士の中で重複しない
// 新規分（fresh）と、重複で除いた件数（skipped）に分ける純粋関数。
function splitImportedPresets(incoming, existing) {
  const seen = new Set(existing.map(presetSignature));
  const fresh = [];
  let skipped = 0;
  for (const p of incoming) {
    const sig = presetSignature(p);
    if (seen.has(sig)) { skipped++; continue; }
    seen.add(sig);
    fresh.push(p);
  }
  return { fresh, skipped };
}

$("song").addEventListener("change", () => { if (playing) startMusic(); });
$("playBtn").addEventListener("click", () => (playing ? stop() : play()));
$("bpm").addEventListener("input", () => {
  cancelTween("bpm");
  clearTimeout(thenTimer);
  thenTimer = null;
  bpmCurrent = Number($("bpm").value);
  $("bpmVal").textContent = $("bpm").value;
});
$("preset").addEventListener("change", () => {
  const s = selectedPreset();
  $("deletePreset").disabled = !(s && s.isUser);
  if (s && s.preset) applyPreset(JSON.parse(JSON.stringify(s.preset)));
});
$("savePreset").addEventListener("click", () => {
  const name = $("presetName").value.trim() || `マイプリセット ${userPresets.length + 1}`;
  userPresets.push({
    name,
    parameters: currentParams(),
    // 保存時の遷移は §4 の初期標準（Ease In Out、30 秒）
    transition: { duration: 30, curve: "easeInOut", parameters: { gain: {}, lowpass: {}, reverb: {} } },
  });
  if (!storeUserPresets()) {
    // 書けなかった場合は成功したように見せない（このセッション限りで消える）
    $("importStatus").textContent = "保存できませんでした（ブラウザの保存容量を超えている可能性があります）";
  }
  refreshPresetOptions();
  $("preset").value = "u:" + (userPresets.length - 1);
  $("deletePreset").disabled = false;
  $("presetName").value = "";
});
$("deletePreset").addEventListener("click", () => {
  const s = selectedPreset();
  if (!s || !s.isUser) return;
  userPresets.splice(s.index, 1);
  if (!storeUserPresets()) {
    $("importStatus").textContent = "削除を保存できませんでした（ブラウザの保存容量を超えている可能性があります）";
  }
  refreshPresetOptions();
});
$("exportPresets").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify({ version: 1, presets: userPresets }, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "lullaby-presets.json";
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
});
$("importPresets").addEventListener("change", async (ev) => {
  const file = ev.target.files && ev.target.files[0];
  ev.target.value = ""; // 同じファイルを選び直せるようにする
  if (!file) return;
  // プリセットは小さな JSON なので、上限を超えるファイルは読む前に弾く
  if (file.size > 1024 * 1024) {
    $("importStatus").textContent = "読み込めませんでした: ファイルが大きすぎます（上限は 1 MB です）";
    return;
  }
  let text;
  try { text = await file.text(); }
  catch (_) {
    $("importStatus").textContent = "読み込めませんでした: ファイルを開けませんでした";
    return;
  }
  const r = parsePresetImport(text);
  if (!r.ok) {
    // 検証に失敗したら何も取り込まず、理由だけを表示する
    $("importStatus").textContent = "読み込めませんでした: " + r.error;
    return;
  }
  // 既に保存済みのもの（と、同じファイルの中で重なったもの）は取り込まない
  const split = splitImportedPresets(r.presets, userPresets);
  if (!split.fresh.length) {
    $("importStatus").textContent = "読み込める新しいプリセットはありませんでした（" + split.skipped + " 件すべて重複）";
    return;
  }
  userPresets.push(...split.fresh);
  if (!storeUserPresets()) {
    // 取り込めても保存できていなければ、その旨を表示する
    $("importStatus").textContent = "読み込みましたが保存できませんでした（ブラウザの保存容量を超えている可能性があります）";
    refreshPresetOptions();
    return;
  }
  refreshPresetOptions();
  $("importStatus").textContent = split.fresh.length + " 件のプリセットを読み込みました" +
    (split.skipped ? "（" + split.skipped + " 件は重複のためスキップ）" : "");
});
initPresets();
// 音量スライダを手で動かしたら、その層の gain 遷移と予約済みの then を
// 取り消す（bpm スライダと同じ扱い。遷移が手動操作を上書きしないように）
[["volMusic", "gain.music"], ["volHeart", "gain.heart"], ["volWaves", "gain.waves"]].forEach(([id, key]) => {
  $(id).addEventListener("input", () => {
    cancelTween(key);
    clearTimeout(thenTimer);
    thenTimer = null;
    applyVolumes();
  });
});
$("timer").addEventListener("change", () => { if (playing) startFadeOut(Number($("timer").value)); });
$("lockBtn").addEventListener("click", () => alert("画面ロックは Phase 3 で実装します"));

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}

// Node の検証ハーネス用に検証関数と状態系の一部を公開する（ブラウザでは module が無いので何もしない）
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    validatePresetData, parsePresetImport, stableStringify, splitImportedPresets,
    loadUserPresets, storeUserPresets, applyPreset, stop,
    getUserPresets: () => userPresets,
    thenTimerPending: () => thenTimer !== null,
  };
}
