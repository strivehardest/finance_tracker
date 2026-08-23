{% load static %}
const CACHE_NAME = 'finance-tracker-v1';
const OFFLINE_URL = '{% url "offline" %}';
const PRECACHE_URLS = [
    OFFLINE_URL,
    '{% static "css/custom.css" %}',
    '{% static "images/pwa-192.png" %}',
    '{% static "images/pwa-512.png" %}',
    '{% static "images/apple-touch-icon.png" %}'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') {
        return;
    }

    const url = new URL(event.request.url);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
        return;
    }

    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request).catch(() => caches.match(OFFLINE_URL))
        );
        return;
    }

    if (url.origin === self.location.origin && url.pathname.startsWith('{{ STATIC_URL }}')) {
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
