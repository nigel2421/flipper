const CACHE_NAME = 'business-matters-v4'; // Increment version
const ASSETS_TO_CACHE = [
    '/',
    '/static/publications/css/style.css',
    '/static/img/logo.png',
    '/static/manifest.json'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // 1. Skip caching for POST requests
    if (event.request.method !== 'GET') {
        return;
    }

    // 2. Skip caching for auth and admin URLs to ensure dynamic behavior
    if (url.pathname.includes('/accounts/') || url.pathname.includes('/admin/')) {
        return;
    }

    // 3. For navigation requests or dynamic pages, use Network First
    if (event.request.mode === 'navigate' || ASSETS_TO_CACHE.includes(url.pathname)) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Update cache with fresh version
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // 4. For other assets, use Cache First
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
