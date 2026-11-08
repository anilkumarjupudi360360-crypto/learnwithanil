// Learn with Anil service worker (8 Nov 2026): lets students install the site as an app and shows a friendly page when offline.
// Pages and files always come from the network (the site changes every day); only a failed page load gets the offline note.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
const OFFLINE = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offline · Learn with Anil</title>'
  + '<body style="margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#F3F6FB;color:#0D1830;display:grid;place-items:center;min-height:100vh;padding:24px;box-sizing:border-box">'
  + '<div style="max-width:420px;text-align:center"><div style="font-size:44px">📶</div><h1 style="font-size:22px">You are offline</h1>'
  + '<p>Connect to the internet and open Learn with Anil again. Your practice and mistakes are saved on this phone.</p>'
  + '<p lang="te">ఇంటర్నెట్ కనెక్ట్ చేసి మళ్లీ తెరవండి.</p><button onclick="location.reload()" style="font:inherit;padding:10px 18px;border-radius:10px;border:0;background:#1846C7;color:#fff">Try again</button></div></body></html>';
self.addEventListener('fetch', e => {
  if (e.request.mode !== 'navigate') return;
  e.respondWith(fetch(e.request).catch(() => new Response(OFFLINE, {headers: {'Content-Type': 'text/html; charset=utf-8'}})));
});
