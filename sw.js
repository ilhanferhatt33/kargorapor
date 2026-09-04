var C='kargorapor-v1';
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(C).then(function(c){
    return c.addAll(['./','./index.html','./manifest.json','./icon-192.png','./icon-512.png']);
  }));
  self.skipWaiting();
});
self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim());});
self.addEventListener('fetch',function(e){
  e.respondWith(caches.match(e.request).then(function(r){return r||fetch(e.request);}));
});
