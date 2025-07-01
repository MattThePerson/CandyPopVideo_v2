const { createProxyMiddleware } = require('http-proxy-middleware');
const express = require('express');
const app = express();

// Serve static files
app.use(express.static(__dirname));

// Custom proxy handler to preserve full path
const proxy = createProxyMiddleware({
    target: 'http://localhost:8011',
    changeOrigin: true,
    pathRewrite: (path, req) => path, // redundant now, but safe
    onProxyRes: (proxyRes) => {
        delete proxyRes.headers['content-security-policy'];
        delete proxyRes.headers['content-security-policy-report-only'];
    },
});

// Manually match paths without stripping them
app.use((req, res, next) => {
    if (req.url.startsWith('/api') || req.url.startsWith('/media') || req.url.startsWith('/terminal')) {
        proxy(req, res, next);
    } else {
        next();
    }
});

// Start server
const PORT = 5123;
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
