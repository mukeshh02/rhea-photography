const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, 'public');

const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.gif': 'image/gif',
  '.avif': 'image/avif',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.ico': 'image/x-icon'
};

http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');

  let file;
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    file = path.resolve(root, '.' + pathname);
    
    // Check fallback for /static.showit.co or /lib.showit.co
    if (!fs.existsSync(file)) {
      const assetFallback = path.resolve(root, 'assets' + pathname);
      if (fs.existsSync(assetFallback)) {
        file = assetFallback;
      }
    }
  } catch {
    res.writeHead(400);
    return res.end('Invalid URL');
  }

  if (file !== root && !file.startsWith(root + path.sep)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  try {
    if (fs.existsSync(file)) {
      if (fs.statSync(file).isDirectory()) {
        const indexFile = path.join(file, 'index.html');
        if (fs.existsSync(indexFile)) {
          file = indexFile;
        }
      }
    } else {
      // If /about requested without trailing slash or directory
      const htmlFile = file + '.html';
      const dirIndex = path.join(file, 'index.html');
      if (fs.existsSync(htmlFile)) {
        file = htmlFile;
      } else if (fs.existsSync(dirIndex)) {
        file = dirIndex;
      }
    }

    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404, {'Content-Type': 'text/plain'});
      return res.end('Not Found');
    }

    const ext = path.extname(file).toLowerCase();
    res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  } catch (err) {
    res.writeHead(500, {'Content-Type': 'text/plain'});
    res.end('Server Error: ' + err.message);
  }
}).listen(process.env.PORT || 3003, '127.0.0.1', () => {
  console.log('Liller Photo website: http://localhost:' + (process.env.PORT || 3003));
});
