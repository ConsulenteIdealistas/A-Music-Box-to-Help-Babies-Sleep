// 監査修正（GitHub Issues #1〜#4, #11）を検証する Node ハーネス。
// DOM / localStorage / WebAudio を最小限スタブして app.js 本体を
// 読み込み、実際のイベントハンドラと公開関数を駆動する。
// 対象:
//   #2 play() の二重実行ガード、startWaves の旧ソース停止、
//      startMusic の世代ガード
//   #3 applyPreset の lowpass は実音の差し替え成功後に確定する
//   #1 保存/削除/取込の永続化失敗時のロールバック
//   #4 loadUserPresets の要素単位検証と理由付き退避
//   #11 保存時の重複排除と自動名の欠番詰め採番
//   既存 ACID 修正の要点（then のキャンセル、破損時の退避）も再確認する
const assert = require("assert");
const path = require("path");

// --- DOM スタブ ---
function makeEl(id) {
  return {
    id, value: "", textContent: "", disabled: false, label: "",
    children: [], listeners: {},
    appendChild(c) { this.children.push(c); return c; },
    addEventListener(type, fn) { (this.listeners[type] || (this.listeners[type] = [])).push(fn); },
  };
}
const els = {};
const documentStub = {
  getElementById(id) { return els[id] || (els[id] = makeEl(id)); },
  createElement(tag) { return makeEl(tag); },
};
// --- localStorage スタブ（失敗を切り替え可能） ---
const store = new Map();
let storageThrows = false;
const localStorageStub = {
  getItem(k) { return store.has(k) ? store.get(k) : null; },
  setItem(k, v) { if (storageThrows) throw new Error("QuotaExceededError (stub)"); store.set(k, String(v)); },
  removeItem(k) { store.delete(k); },
};
// --- WebAudio スタブ ---
const liveSources = new Set(); // start されて stop されていない BufferSource
function paramStub() {
  return {
    value: 0,
    setValueAtTime() {}, linearRampToValueAtTime() {}, setTargetAtTime() {},
    setValueCurveAtTime() {}, cancelScheduledValues() {},
  };
}
function nodeStub() { return { connect(t) { return t; }, disconnect() {} }; }
function gainStub() { return Object.assign(nodeStub(), { gain: paramStub() }); }
function srcStub() {
  return {
    buffer: null, loop: false, stopped: false,
    connect(t) { return t; }, disconnect() {},
    start() { liveSources.add(this); },
    stop() { this.stopped = true; liveSources.delete(this); },
  };
}
function oscStub() {
  return Object.assign(nodeStub(), { type: "", frequency: paramStub(), start() {}, stop() {} });
}
// 曲ごとの「デコード済み音源」: 長さで曲を識別する
const RAW_LEN = { A: 44100, B: 88200, C: 132300 };
class FakeCtx {
  constructor() {
    FakeCtx.last = this;
    this.sampleRate = 44100;
    this.currentTime = 0;
    this.state = "running";
    this.destination = nodeStub();
    this.resumeCount = 0;
  }
  createGain() { return gainStub(); }
  createOscillator() { return oscStub(); }
  createBuffer(ch, len, sr) {
    const data = new Float32Array(len);
    return { duration: len / sr, getChannelData() { return data; } };
  }
  createBufferSource() { return srcStub(); }
  async decodeAudioData(ab) {
    const len = RAW_LEN[ab.songKey] || 44100;
    const data = new Float32Array(len).fill(0.3);
    return { duration: len / 44100, getChannelData() { return data; } };
  }
  async resume() { this.resumeCount++; }
  async suspend() {}
}
// --- fetch スタブ（URL ごとに遅延と失敗を切り替える） ---
const fetchDelayMs = { brahms: 0, moldau: 0, vissi: 60, yurikago: 0 };
let fetchFailsWav = false;
async function fetchStub(url) {
  const u = String(url);
  if (u.includes("presets.json")) {
    return { ok: true, json: async () => ({ version: 1, presets: [{ name: "標準", parameters: { bpm: 70 } }] }) };
  }
  if (u.endsWith(".wav")) {
    if (fetchFailsWav) throw new Error("fetch stub: wav failure");
    const key = Object.keys(fetchDelayMs).find((k) => u.includes(k));
    const songKey = { brahms: "A", moldau: "B", vissi: "C", yurikago: "A" }[key] || "A";
    await new Promise((r) => setTimeout(r, fetchDelayMs[key] || 0));
    return { ok: true, arrayBuffer: async () => ({ songKey }) };
  }
  throw new Error("fetch stub: unknown url " + u);
}
function defGlobal(name, value) {
  try { Object.defineProperty(globalThis, name, { value, configurable: true, writable: true }); }
  catch (_) { globalThis[name] = value; }
}
defGlobal("document", documentStub);
defGlobal("localStorage", localStorageStub);
defGlobal("navigator", {});
defGlobal("fetch", fetchStub);
defGlobal("AudioContext", FakeCtx);
defGlobal("window", { AudioContext: FakeCtx });

const app = require(path.join(__dirname, "..", "app.js"));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const el = (id) => documentStub.getElementById(id);
const click = (id) => el(id).listeners.click[0]();
const liveByDuration = (s) => [...liveSources].filter((x) => x.buffer && Math.abs(x.buffer.duration - s) < 0.01);

let passed = 0, failed = 0;
async function test(name, fn) {
  try { await fn(); passed++; console.log("PASS:", name); }
  catch (e) { failed++; console.log("FAIL:", name, "-", e.message); }
}

(async () => {
  await sleep(50); // initPresets の落ち着き待ち
  el("song").value = "brahms";
  el("timer").value = "0";
  el("volMusic").value = "80"; el("volHeart").value = "80"; el("volWaves").value = "80";

  // ---------- Issue #2 ----------
  await test("#2 play() の二重実行はガードされる（resume は1回だけ）", async () => {
    await app.play();
    await sleep(30);
    const ctx = FakeCtx.last;
    const n = ctx.resumeCount;
    await app.play();
    assert.strictEqual(ctx.resumeCount, n, "2回目の play() で resume が増えていない");
    assert.strictEqual(liveByDuration(8).length, 1, "waves ソースは1つ");
    assert.strictEqual(liveByDuration(1).length, 1, "music ソースは1つ");
  });

  await test("#2 startWaves() を再び呼んでも旧ソースが止まり、waves は1つのまま", async () => {
    const before = liveByDuration(8)[0];
    app.startWaves();
    assert.strictEqual(liveByDuration(8).length, 1, "waves ソースは1つ");
    assert.ok(before.stopped, "旧 waves ソースが stop されている");
  });

  await test("#2 startMusic() の解決順が入れ替わっても、最後に選んだ曲が残る", async () => {
    el("song").value = "vissi"; // 遅い (60ms, 3秒バッファ)
    const p1 = app.startMusic();
    el("song").value = "moldau"; // 速い (0ms, 2秒バッファ)
    const p2 = app.startMusic();
    await Promise.all([p1, p2]);
    await sleep(120);
    assert.strictEqual(liveByDuration(2).length, 1, "モルダウ (2秒) が鳴っている");
    assert.strictEqual(liveByDuration(3).length, 0, "歌に生き (3秒) は残っていない");
  });

  // ---------- Issue #3 ----------
  await test("#3 lowpass は差し替え成功後にだけ確定する", async () => {
    assert.strictEqual(app.getLowpassHz(), 250, "初期値は 250");
    app.applyPreset({ name: "t", parameters: { lowpassHz: 500 }, transition: { duration: 0 } });
    await sleep(50);
    assert.strictEqual(app.getLowpassHz(), 500, "成功後は 500 に確定");
    assert.strictEqual(el("lpVal").textContent, 500);
  });

  await test("#3 lowpass の差し替えが失敗したら宣言状態は旧値のまま", async () => {
    fetchFailsWav = true;
    app.applyPreset({ name: "t", parameters: { lowpassHz: 700 }, transition: { duration: 0 } });
    await sleep(50);
    fetchFailsWav = false;
    assert.strictEqual(app.getLowpassHz(), 500, "失敗時は 500 のまま");
    assert.strictEqual(el("lpVal").textContent, 500, "表示も旧値のまま");
  });

  // ---------- 既存 ACID 修正の再確認 ----------
  await test("ACID then は stop() で取り消される", async () => {
    app.applyPreset({
      name: "t", parameters: { bpm: 66 }, transition: { duration: 0 },
      then: { parameters: { bpm: 60 }, transition: { duration: 0 } },
    });
    assert.ok(app.thenTimerPending(), "then が予約されている");
    app.stop();
    assert.ok(!app.thenTimerPending(), "stop() で then が取り消された");
    await sleep(20);
  });

  // ---------- プリセット保存まわり（#1 / #11）の準備 ----------
  const resetPresets = (json) => {
    store.set("lullaby.presets", json);
    app.loadUserPresets();
  };
  resetPresets("[]");
  assert.strictEqual(app.getUserPresets().length, 0);

  await test("#11 同じ内容は二重保存されず、自動名は欠番を詰める", async () => {
    el("presetName").value = "";
    click("savePreset");
    assert.strictEqual(app.getUserPresets().length, 1);
    assert.strictEqual(app.getUserPresets()[0].name, "マイプリセット 1");
    click("savePreset"); // 同じ状態でもう一度
    assert.strictEqual(app.getUserPresets().length, 1, "重複保存されていない");
    assert.ok(el("importStatus").textContent.includes("既に保存されています"), el("importStatus").textContent);
    el("volMusic").value = "50";
    click("savePreset");
    assert.strictEqual(app.getUserPresets().length, 2);
    assert.strictEqual(app.getUserPresets()[1].name, "マイプリセット 2");
    // 1番を消してから保存すると、名前は 3 ではなく空いた 1 になる
    el("preset").value = "u:0";
    click("deletePreset");
    assert.strictEqual(app.getUserPresets().length, 1);
    el("volMusic").value = "70";
    click("savePreset");
    assert.strictEqual(app.getUserPresets().length, 2);
    assert.strictEqual(app.getUserPresets()[1].name, "マイプリセット 1", "欠番が詰められている");
  });

  await test("#1 保存の永続化に失敗したらメモリ上も巻き戻る", async () => {
    el("volMusic").value = "33";
    storageThrows = true;
    click("savePreset");
    storageThrows = false;
    assert.strictEqual(app.getUserPresets().length, 2, "失敗した保存は残っていない");
    assert.ok(el("importStatus").textContent.includes("保存できませんでした"));
  });

  await test("#1 削除の永続化に失敗したらメモリ上も巻き戻る", async () => {
    el("preset").value = "u:0";
    storageThrows = true;
    click("deletePreset");
    storageThrows = false;
    assert.strictEqual(app.getUserPresets().length, 2, "失敗した削除は巻き戻っている");
    assert.ok(el("importStatus").textContent.includes("削除を保存できませんでした"));
  });

  await test("#1 取込の永続化に失敗したら巻き戻り、復旧後は同じファイルを読み込める", async () => {
    const handler = el("importPresets").listeners.change[0];
    const text = JSON.stringify({ version: 1, presets: [{ name: "取込X", parameters: { bpm: 61 }, transition: { duration: 5, curve: "linear" } }] });
    const file = { size: text.length, text: async () => text };
    storageThrows = true;
    await handler({ target: { files: [file], value: "dummy" } });
    storageThrows = false;
    assert.strictEqual(app.getUserPresets().length, 2, "失敗した取込は残っていない");
    assert.ok(el("importStatus").textContent.includes("読み込みを取り消しました"), el("importStatus").textContent);
    await handler({ target: { files: [file], value: "dummy" } });
    assert.strictEqual(app.getUserPresets().length, 3, "復旧後は同じファイルを読み込める（重複判定に残っていない）");
  });

  // ---------- Issue #4 ----------
  await test("#4 読み込み時に壊れた要素だけが理由付きで退避される", async () => {
    const good1 = { name: "正常1", parameters: { bpm: 70 } };
    const good2 = { name: "正常2", parameters: { bpm: 72 } };
    resetPresets(JSON.stringify([good1, { name: 5 }, "junk", good2]));
    const names = app.getUserPresets().map((p) => p.name);
    assert.deepStrictEqual(names, ["正常1", "正常2"], "健全な要素だけが残る");
    const rej = JSON.parse(store.get("lullaby.presets.rejected"));
    assert.strictEqual(rej.rejected.length, 2, "壊れた2件が退避されている");
    assert.ok(rej.rejected.every((r) => typeof r.error === "string" && r.error), "理由が付いている");
    assert.ok(el("importStatus").textContent.includes("退避しました"), el("importStatus").textContent);
  });

  await test("ACID 壊れた JSON は corrupt キーに退避される（従来どおり）", async () => {
    resetPresets("{broken json");
    assert.strictEqual(app.getUserPresets().length, 0);
    assert.strictEqual(store.get("lullaby.presets.corrupt"), "{broken json");
  });

  console.log("\n結果: " + passed + " passed, " + failed + " failed");
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error(" harness error:", e); process.exit(1); });
