"use strict";
/*
 * lullaby-pwa スケルトン
 * Web Audio API 単体で 3 層（オルゴール / 心音 / さざ波）の
 * グラフとミキサーを配線しただけの器。音源とパラメータは
 * Phase 1（文献レビュー）・Phase 2（音源制作）で差し込む。
 *
 * TODO(Phase 2): オルゴールはステム音源のシームレスループに差し替え
 * TODO(Phase 1): 最大音量リミッター値をレビューの安全側統計から設定
 * TODO: エントレインメント減速カーブ（BPM 85 → 65）、キー変更、画面ロック
 */

let ctx = null;
let master, gainMusic, gainHeart, gainWaves;
let heartTimer = null, fadeTimer = null, wavesNodes = null;
let playing = false;

const $ = (id) => document.getElementById(id);

function buildGraph() {
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  master = ctx.createGain();
  master.gain.value = 0.9; // TODO: リミッター（Phase 1 で確定）
  master.connect(ctx.destination);

  gainMusic = ctx.createGain();
  gainHeart = ctx.createGain();
  gainWaves = ctx.createGain();
  gainMusic.connect(master);
  gainHeart.connect(master);
  gainWaves.connect(master);
  applyVolumes();
}

// --- 心音: 低いサイン波の2拍（lub-dub）をスケジュールする仮実装 ---
function thump(when, freq, peak, dur) {
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = "sine";
  osc.frequency.value = freq;
  g.gain.setValueAtTime(0, when);
  g.gain.linearRampToValueAtTime(peak, when + 0.02);
  g.gain.exponentialRampToValueAtTime(0.001, when + dur);
  osc.connect(g).connect(gainHeart);
  osc.start(when);
  osc.stop(when + dur + 0.05);
}
function scheduleHeart() {
  clearTimeout(heartTimer);
  if (!playing) return;
  const bpm = Number($("bpm").value);
  const period = 60 / bpm;
  const t = ctx.currentTime + 0.05;
  thump(t, 58, 0.9, 0.18);            // 第1音
  thump(t + period * 0.28, 50, 0.55, 0.14); // 第2音
  heartTimer = setTimeout(scheduleHeart, period * 1000);
}

// --- さざ波: ブラウンノイズ → ローパス → ゆっくりした音量ゆらぎ ---
function startWaves() {
  const len = ctx.sampleRate * 4;
  const buf = ctx.createBuffer(1, len, ctx.sampleRate);
  const d = buf.getChannelData(0);
  let last = 0;
  for (let i = 0; i < len; i++) {
    const white = Math.random() * 2 - 1;
    last = (last + 0.02 * white) / 1.02;
    d[i] = last * 3.2;
  }
  const src = ctx.createBufferSource();
  src.buffer = buf;
  src.loop = true;
  const lpf = ctx.createBiquadFilter();
  lpf.type = "lowpass";
  lpf.frequency.value = 500; // DESIGN.md §2: 200〜500Hz 中心（仮説値）
  const lfo = ctx.createOscillator();
  lfo.frequency.value = 0.08; // 血流音に近い周期的なゆらぎ（仮）
  const lfoGain = ctx.createGain();
  lfoGain.gain.value = 0.25;
  const swell = ctx.createGain();
  swell.gain.value = 0.75;
  lfo.connect(lfoGain).connect(swell.gain);
  src.connect(lpf).connect(swell).connect(gainWaves);
  src.start();
  lfo.start();
  wavesNodes = { src, lfo };
}
function stopWaves() {
  if (!wavesNodes) return;
  try { wavesNodes.src.stop(); wavesNodes.lfo.stop(); } catch (_) {}
  wavesNodes = null;
}

// --- オルゴール: Phase 2 でステム音源を接続する。現状は無音 ---
// gainMusic は配線済み。音源が入るまではスライダーだけが効く。

function applyVolumes() {
  if (!ctx) return;
  gainMusic.gain.value = $("volMusic").value / 100;
  gainHeart.gain.value = $("volHeart").value / 100;
  gainWaves.gain.value = $("volWaves").value / 100;
}

function startFadeOut(minutes) {
  clearTimeout(fadeTimer);
  if (!minutes) return;
  fadeTimer = setTimeout(() => {
    const t = ctx.currentTime;
    master.gain.cancelScheduledValues(t);
    master.gain.setValueAtTime(master.gain.value, t);
    master.gain.linearRampToValueAtTime(0, t + 30); // 終了30秒前からフェード
    setTimeout(stop, 31000);
  }, (minutes * 60 - 30) * 1000);
}

async function play() {
  if (!ctx) buildGraph();
  await ctx.resume();
  playing = true;
  master.gain.value = 0.9;
  scheduleHeart();
  startWaves();
  startFadeOut(Number($("timer").value));
  $("playBtn").textContent = "■ 停止";
}
function stop() {
  playing = false;
  clearTimeout(heartTimer);
  clearTimeout(fadeTimer);
  stopWaves();
  if (ctx) ctx.suspend();
  $("playBtn").textContent = "▶ 再生";
}

$("playBtn").addEventListener("click", () => (playing ? stop() : play()));
$("bpm").addEventListener("input", () => { $("bpmVal").textContent = $("bpm").value; });
["volMusic", "volHeart", "volWaves"].forEach((id) => $(id).addEventListener("input", applyVolumes));
$("timer").addEventListener("change", () => { if (playing) startFadeOut(Number($("timer").value)); });
$("lockBtn").addEventListener("click", () => alert("画面ロックは Phase 3 で実装します"));

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}
