const C="jarvis-v1",F=["./","index.html","manifest.json","icon.svg"];
self.addEventListener("install",e=>e.waitUntil(caches.open(C).then(c=>c.addAll(F))));
self.addEventListener("fetch",e=>{if(e.request.url.includes("anthropic.com"))return;
e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))});
