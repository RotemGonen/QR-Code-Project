const http = require('http');

const PORT = 80;

const server = http.createServer((req, res) => {
      res.statusCode = 200;
      res.setHeader('Content-Type', 'text/plain');
      res.end('Hello, World!\n');
});

server.listen(PORT, () => {
      console.log(`Server running at http://localhost:${PORT}/`);
});
