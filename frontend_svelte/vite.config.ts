import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        tailwindcss(), // before Svelte
        svelte(),
    ],
    // server: {
    //     "port": 32115, // Wails default
    // },
})
