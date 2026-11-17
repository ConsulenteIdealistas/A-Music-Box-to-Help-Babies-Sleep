// プリセット読み込みの重複排除を検証する Node ハーネス。
// DOM / localStorage を最小限スタブして app.js 本体を読み込み、
// importPresets の change ハンドラを実際に駆動する。
const assert = require("assert");

// --- スタブ ---
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
const store = new Map();
let storageThrows = false;
const localStorageStub = {
  getItem(k) { return store.has(k) ? store.get(k) : null; },
  setItem(k, v) { if (storageThrows) throw new Error("QuotaExceededError (stub)"); store.set(k, String(v)); },
  removeItem(k) { store.delete(k); },
};
function defGlobal(name, value) {
  try { Object.defineProperty(globalThis, name, { value, configurable: true, writable: true }); }
  catch (_) { globalThis[name] = value; }
}
defGlobal("document", documentStub);
defGlobal("localStorage", localStorageStub);
defGlobal("navigator", {});
defGlobal("fetch", async () => { throw new Error("fetch stub: offline"); });

const app = require(require("path").join(__dirname, "..", "app.js"));

// --- フィクスチャ（保存時の形式に合わせる） ---
const TR = { duration: 30, curve: "easeInOut", parameters: { gain: {}, lowpass: {}, reverb: {} } };
const A = { name: "テストA", parameters: { bpm: 70, gain: { music: 80, heart: 80, waves: 80 }, lowpassHz: 250 }, transition: TR };
const B = { name: "テストB", parameters: { bpm: 68 }, transition: TR };
const C = { name: "テストC", parameters: { gain: { waves: 100 } }, transition: { duration: 10, curve: "easeInOut", parameters: { gain: {}, lowpass: {}, reverb: {} } } };
const D = {
  name: "テストD", parameters: { bpm: 88, gain: { waves: 100 } },
  then: { parameters: { bpm: 65 }, transition: { duration: 180, curve: "easeInOut", parameters: { gain: {}, lowpass: {}, reverb: {} } } },
  transition: { duration: 10, curve: "easeInOut", parameters: { gain: {}, lowpass: {}, reverb: {} } },
};
const fileOf = (presets) => JSON.stringify({ version: 1, presets });

async function doImport(text) {
  const handler = els.importPresets.listeners.change[0];
  assert.ok(handler, "import change handler が登録されている");
  const file = { size: text.length, text: async () => text };
  await handler({ target: { files: [file], value: "dummy" } });
  return els.importStatus.textContent;
}

let passed = 0, failed = 0;
async function test(name, fn) {
  try { await fn(); passed++; console.log("PASS:", name); }
  catch (e) { failed++; console.log("FAIL:", name, "-", e.message); }
}

(async () => {
  // initPresets（fetch スタブで失敗経路）が落ち着くのを待つ
  await new Promise((r) => setTimeout(r, 100));
  assert.strictEqual(app.getUserPresets().length, 0, "初期状態は空");

  await test("1. 同じファイルを2回読み込むと、2回目は全件重複で追加0", async () => {
    const msg1 = await doImport(fileOf([A, B]));
    assert.strictEqual(app.getUserPresets().length, 2);
    assert.strictEqual(msg1, "2 件のプリセットを読み込みました");
    const msg2 = await doImport(fileOf([A, B]));
    assert.strictEqual(app.getUserPresets().length, 2, "2回目で増えていない");
    assert.strictEqual(msg2, "読み込める新しいプリセットはありませんでした（2 件すべて重複）");
  });

  await test("2. 重複1件＋新規1件のファイルは、新規の1件だけ追加される", async () => {
    const msg = await doImport(fileOf([A, C]));
    assert.strictEqual(app.getUserPresets().length, 3);
    assert.strictEqual(msg, "1 件のプリセットを読み込みました（1 件は重複のためスキップ）");
  });

  await test("3. ファイル内部の重複は1件だけ取り込まれる", async () => {
    const msg = await doImport(fileOf([D, D]));
    assert.strictEqual(app.getUserPresets().length, 4);
    assert.strictEqual(msg, "1 件のプリセットを読み込みました（1 件は重複のためスキップ）");
  });

  await test("4. キーの並び順が違うだけの同一内容も重複と判定される", async () => {
    const reordered = '{"version":1,"presets":[{"transition":{"parameters":{"reverb":{},"lowpass":{},"gain":{}},"curve":"easeInOut","duration":30},"parameters":{"lowpassHz":250,"gain":{"waves":80,"heart":80,"music":80},"bpm":70},"name":"テストA"}]}';
    const msg = await doImport(reordered);
    assert.strictEqual(app.getUserPresets().length, 4, "キー順違いで増えていない");
    assert.strictEqual(msg, "読み込める新しいプリセットはありませんでした（1 件すべて重複）");
  });

  await test("5. 名前が同じでも内容が違えば重複ではない", async () => {
    const A2 = JSON.parse(JSON.stringify(A)); A2.parameters.bpm = 71;
    const msg = await doImport(fileOf([A2]));
    assert.strictEqual(app.getUserPresets().length, 5);
    assert.strictEqual(msg, "1 件のプリセットを読み込みました");
  });

  await test("6a. 不正な curve 名はファイル全体を拒否する（従来どおり）", async () => {
    const bad = { name: "不良", parameters: { bpm: 70 }, transition: { duration: 10, curve: "bounce" } };
    const msg = await doImport(fileOf([bad]));
    assert.strictEqual(app.getUserPresets().length, 5);
    assert.ok(msg.startsWith("読み込めませんでした: "), msg);
  });

  await test("6b. parameters の無いプリセットは拒否する（従来どおり）", async () => {
    const msg = await doImport(fileOf([{ name: "不良2" }]));
    assert.strictEqual(app.getUserPresets().length, 5);
    assert.ok(msg.startsWith("読み込めませんでした: "), msg);
  });

  await test("6c. 壊れた JSON は拒否する（従来どおり）", async () => {
    const msg = await doImport("{not json");
    assert.strictEqual(app.getUserPresets().length, 5);
    assert.ok(msg.startsWith("読み込めませんでした: "), msg);
  });

  await test("7. 永続化に失敗したら取込は巻き戻る（Issue #1 で表示のみから変更）", async () => {
    storageThrows = true;
    const E = { name: "テストE", parameters: { bpm: 60 }, transition: TR };
    const msg = await doImport(fileOf([E]));
    storageThrows = false;
    assert.ok(msg.startsWith("保存できなかったため、読み込みを取り消しました"), msg);
    assert.strictEqual(app.getUserPresets().length, 5, "失敗した取込はメモリにも残っていない");
    const msg2 = await doImport(fileOf([E]));
    assert.strictEqual(app.getUserPresets().length, 6, "復旧後は同じファイルを読み込める");
    assert.strictEqual(msg2, "1 件のプリセットを読み込みました");
  });

  await test("8. splitImportedPresets 単体: then の差異も重複判定に効く", async () => {
    const D2 = JSON.parse(JSON.stringify(D)); D2.then.parameters.bpm = 66;
    const r = app.splitImportedPresets([D2], app.getUserPresets());
    assert.strictEqual(r.fresh.length, 1, "then が違えば新規");
    assert.strictEqual(r.skipped, 0);
    const r2 = app.splitImportedPresets([JSON.parse(JSON.stringify(D))], app.getUserPresets());
    assert.strictEqual(r2.fresh.length, 0, "then まで同一なら重複");
    assert.strictEqual(r2.skipped, 1);
  });

  console.log("\n結果: " + passed + " passed, " + failed + " failed");
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error(" harness error:", e); process.exit(1); });
