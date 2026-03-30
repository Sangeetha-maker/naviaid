import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'logo192.png'],
      manifest: {
        name: 'NaviAid – Government Scheme Finder',
        short_name: 'NaviAid',
        description: 'Find scholarships, jobs, health schemes for Tamil Nadu residents',
        theme_color: '#2563eb',
        background_color: '#0f172a',
        display: 'standalone',
        start_url: '/',
        lang: 'ta',
        icons: [
          { src: '/logo192.png', sizes: '192x192', type: 'image/png' },
          { src: '/logo512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*\/reco\/.*/i,
            handler: 'NetworkFirst',
            options: { cacheName: 'reco-cache', expiration: { maxEntries: 50, maxAgeSeconds: 3600 } },
          },
          {
            urlPattern: /^https:\/\/.*\/search\/.*/i,
            handler: 'NetworkFirst',
            options: { cacheName: 'search-cache', expiration: { maxEntries: 100, maxAgeSeconds: 1800 } },
          },
        ],
      },
    }),
  ],
  server: { port: 5173, host: '0.0.0.0' },
})
