var C='kargorapor-v1';
var C='kargorapor-v2';
var CORE=['./','./index.html','./manifest.json','./icon-192.png','./icon-512.png','./legal.css'];

self.addEventListener('install',function(e){
  e.waitUntil(caches.open(C).then(function(c){return c.addAll(CORE);}));
  self.skipWaiting();
});

self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(keys){
    return Promise.all(keys.filter(function(key){return key!==C;}).map(function(key){return caches.delete(key);}));
  }).then(function(){return self.clients.claim();}));
});

self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;
  if(e.request.mode==='navigate'){
    e.respondWith(fetch(e.request).then(function(response){
      var copy=response.clone();caches.open(C).then(function(cache){cache.put(e.request,copy);});return response;
    }).catch(function(){return caches.match(e.request).then(function(hit){return hit||caches.match('./index.html');});}));
    return;
  }
  e.respondWith(caches.match(e.request).then(function(hit){return hit||fetch(e.request);}));
});
