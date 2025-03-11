const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
  // 1. HTTPメソッドの制限 (GETのみ許可)
  if (req.method !== 'GET') {
    res.writeHead(405, { 'Content-Type': 'text/plain' });
    res.end('Method Not Allowed');
    return;
  }

  // 2. リクエストされたパスを正規化してディレクトリトラバーサルを防止
  let basePath = req.url.split('?')[0]; // '?' より前の部分だけを取得
  let filePath = path.join(__dirname, basePath === '/' ? '/home/index.html' : basePath);

  // パスがサーバーのドキュメントルートを超えないようにする
  filePath = path.normalize(filePath);  // 不正なパスを正規化
  if (!filePath.startsWith(__dirname)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  // 3. 拡張子が.htmlであることを確認
  const extname = path.extname(filePath).toLowerCase();
  if (extname !== '.html') {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
    return;
  }

  // 4. ファイルを読み込む
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('404 Not Found');
    } else {
      // 5. セキュリティヘッダーを追加
      res.setHeader('X-Content-Type-Options', 'nosniff');  // MIMEスニッフィングを防止
      res.setHeader('Content-Security-Policy', "default-src 'self'");  // 自サイト内のみ許可
      res.setHeader('X-Frame-Options', 'DENY');  // クロスサイトスクリプティング（XSS）対策

      // 6. レスポンスを返す
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    }
  });
});

// 7. サーバーのリスニングポートを設定
server.listen(3000, () => {
  console.log('Server running at http://localhost:3000/');
});
