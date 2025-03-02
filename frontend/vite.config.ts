import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
// import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [
		sveltekit(),
		// tailwindcss(),
	],
	server: {
		proxy: {
			'^/(api|media|video|search|dashboard)(/.*)?$': { // proxy all requests
				target: 'http://localhost:8000', // Backend server
				changeOrigin: true,
				rewrite: (path) => path, // Forward the full path
			},
		},
	},
});
