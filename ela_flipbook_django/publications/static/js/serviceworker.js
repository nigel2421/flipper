const CACHE_NAME = 'business-matters-v6'; // Bump: fix invisible lazy images + loader
const ASSETS_TO_CACHE = [
    '/',
    '/static/publications/css/style.css?v=5.2',
    '/static/publications/css/tailwind.css?v=5.1',
    '/static/img/logo.png',
    '/static/manifest.json'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        }).then(() => self.skipWaiting())
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
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Never intercept ads, analytics, fonts, or media on GCS —
    // cross-origin image caching was a common cause of blank covers.
    if (
        url.hostname.includes('doubleclick.net') ||
        url.hostname.includes('googlesyndication.com') ||
        url.hostname.includes('googletagservices.com') ||
        url.hostname.includes('google-analytics.com') ||
        url.hostname.includes('googletagmanager.com') ||
        url.hostname.includes('storage.googleapis.com') ||
        url.hostname.includes('googleapis.com') ||
        url.hostname.includes('gstatic.com') ||
        url.hostname.includes('cdn.tailwindcss.com') ||
        url.hostname.includes('cdnjs.cloudflare.com') ||
        url.hostname.includes('fonts.googleapis.com') ||
        url.hostname.includes('fonts.gstatic.com')
    ) {
        return;
    }

    // Skip caching for POST requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip caching for auth and admin URLs
    if (url.pathname.includes('/accounts/') || url.pathname.includes('/admin/')) {
        return;
    }

    // Navigation / shell: Network First
    if (event.request.mode === 'navigate' || ASSETS_TO_CACHE.includes(url.pathname)) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
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

    // Same-origin static assets: Cache First
    if (url.origin === self.location.origin) {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request);
            })
        );
    }
});
