import devtoolsJson from 'vite-plugin-devtools-json';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit(), devtoolsJson()],
	server: {
        proxy: {
            '^/(api|media|terminal)(/.*)?$': { // proxy all requests 
				target: 'http://localhost:8000', // Backend server
				changeOrigin: true,
				rewrite: (path) => path, // Forward the full path
			},
        },
    },
});
