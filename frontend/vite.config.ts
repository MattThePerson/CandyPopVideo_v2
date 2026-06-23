import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        tailwindcss(), // before Svelte
        svelte(),
    ],
    resolve: {
        alias: {
            '$lib': path.resolve('./src/lib'),
        },
    },
    server: {
        proxy: {
            '/api':    'http://localhost:8124',
            '/media':  'http://localhost:8124',
            '/static': 'http://localhost:8124',
        },
    },
})
