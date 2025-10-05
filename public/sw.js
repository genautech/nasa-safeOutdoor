const CACHE_NAME = "safe-outdoor-v3"
const OFFLINE_ASSETS = ["/", "/favicon.ico", "/manifest.json"].filter(Boolean)

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(OFFLINE_ASSETS).catch(() => undefined)
    }),
  )
})

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((staleKey) => caches.delete(staleKey)),
      ),
    ),
  )
  return self.clients.claim()
})

self.addEventListener("fetch", (event) => {
  const request = event.request

  if (request.method !== "GET") {
    return
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        const cloned = response.clone()
        caches.open(CACHE_NAME).then((cache) => cache.put(request, cloned)).catch(() => undefined)
        return response
      })
      .catch(() => caches.match(request).then((cached) => cached || caches.match("/"))),
  )
})
