// Service Worker: アプリシェルをキャッシュして完全オフライン動作させる。
const CACHE = "lullaby-shell-v4";
// コアシェルは addAll で一括に入れる。presets.json は正本データ側なので
// 分けて入れ、取得に失敗してもシェル全体のインストールを巻き込まない
// （標準プリセットが無い状態でもアプリは起動し、アプリ側が表示で知らせる）。
const SHELL = ["./", "./index.html", "./style.css", "./app.js", "./manifest.webmanifest"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(SHELL).then(() => c.add("./presets.json").catch(() => {})))
      .then(() => self.skipWaiting())
  );
});
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
});
