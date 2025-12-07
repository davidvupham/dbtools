const http = require('http');

const server = http.createServer((req, res) => {
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'healthy', user: process.env.USER || 'unknown' }));
        return;
    }

    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`Hello from a secure container!\nRunning as: ${process.env.USER || 'unknown'}\n`);
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
});
