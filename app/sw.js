// Service Worker: アプリシェルをキャッシュして完全オフライン動作させる。
const CACHE = "lullaby-shell-v6";
// 音源（assets/*.wav）はシェルとは別の任意キャッシュに入れる。
// シェルの版を上げても消えず、取得の失敗がシェルの導入を巻き込まない。
const ASSETS_CACHE = "lullaby-assets-v1";
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
      .then((keys) => Promise.all(
        // 旧シェルだけを消す（音源キャッシュは残す）
        keys.filter((k) => k.startsWith("lullaby-shell-") && k !== CACHE).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.includes("/assets/") && url.pathname.endsWith(".wav")) {
    // 音源は任意キャッシュ（失敗許容）: 一度取得できたら次回から
    // オフラインでも使える。キャッシュにもネットワークにも無ければ
    // reject せず 503 を返し、アプリ側の表示に委ねる。
    e.respondWith(
      caches.open(ASSETS_CACHE).then(async (c) => {
        const hit = await c.match(e.request);
        if (hit) return hit;
        try {
          const res = await fetch(e.request);
          if (res.ok) c.put(e.request, res.clone());
          return res;
        } catch (_) {
          return new Response("offline: asset not cached", { status: 503, statusText: "Offline" });
        }
      })
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then((hit) => hit || fetch(e.request).catch(
      () => new Response("offline", { status: 503, statusText: "Offline" })
    ))
  );
});
