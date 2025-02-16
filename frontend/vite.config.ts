import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'^/(.*)': { // proxy all requests
				target: 'http://localhost:8000', // Backend server
				changeOrigin: true,
				rewrite: (path) => path, // Forward the full path
			},
		},
	},
});