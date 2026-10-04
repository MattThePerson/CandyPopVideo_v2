import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { VitePWA } from 'vite-plugin-pwa'
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(), // before Svelte
    svelte(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'CandyPop Video',
        short_name: 'cpop vids',
        start_url: '/search',
        display: 'standalone',
        background_color: '#222222',
        theme_color: '#cc22bb',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      // lets you test installability with `npm run dev`
      devOptions: { enabled: true },
    }),
  ], /* plugins */
  resolve: {
    alias: {
      '$lib': path.resolve('./src/lib'),
    },
  },
  server: {
    proxy: {
      '/api':            'http://localhost:8124',
      '/media':          'http://localhost:8124',
      '/static':         'http://localhost:8124',
      '/curated-sites':  'http://localhost:8124',
    },
  },
})
