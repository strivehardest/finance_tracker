const CACHE_NAME = 'finance-tracker-v5';
const OFFLINE_URL = '{{ offline_url }}';
const PRECACHE_URLS = [
    OFFLINE_URL,
    '{{ icon_192_url }}',
    '{{ icon_512_url }}'
];

self.addEventListener('install', (event) => {
    event.waitUntil((async () => {
        const cache = await caches.open(CACHE_NAME);
        await Promise.all(PRECACHE_URLS.map(async (url) => {
            try {
                await cache.add(url);
            } catch (err) {
                // Missing assets must not block install.
            }
        }));
        await self.skipWaiting();
    })());
});

self.addEventListener('activate', (event) => {
    event.waitUntil((async () => {
        const keys = await caches.keys();
        await Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)));
        await self.clients.claim();
    })());
});

self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') {
        return;
    }

    const url = new URL(event.request.url);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
        return;
    }

    if (event.request.mode === 'navigate' || url.pathname === '/app.css' || url.pathname.endsWith('.css')) {
        event.respondWith(
            fetch(event.request).catch(() => caches.match(event.request.mode === 'navigate' ? OFFLINE_URL : event.request))
        );
        return;
    }

    const isAppAsset = url.origin === self.location.origin && (
        url.pathname.startsWith('{{ STATIC_URL }}') ||
        url.pathname.startsWith('/pwa/') ||
        url.pathname === '/favicon.ico' ||
        url.pathname === '/apple-touch-icon.png'
    );

    if (isAppAsset) {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                if (cached) {
                    return cached;
                }
                return fetch(event.request).then((response) => {
                    if (response && response.ok) {
                        const copy = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
                    }
                    return response;
                });
            })
        );
    }
});
