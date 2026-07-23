const http = require('http');
const url = require('url');

http.createServer((req, res) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
        console.log('📩 Datos recibidos:');
        console.log('Método:', req.method);
        console.log('URL:', req.url);
        console.log('Headers:', req.headers);
        console.log('Body:', body);
        console.log('---');
        res.writeHead(200);
        res.end('OK');
    });
}).listen(4444, () => {
    console.log('🚀 Servidor escuchando en puerto 4444');
    console.log('📡 Conecta ngrok: ngrok http 4444');
});
