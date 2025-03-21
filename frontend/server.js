const http = require('http');
const fs = require('fs');
const path = require('path');

// 環境変数を読み込む
const accountHost = process.env.ACCOUNT_HOST || '';
const tournamentHost = process.env.TOURNAMENT_HOST || '';
const gameHost = process.env.GAME_HOST || '';

const server = http.createServer((req, res) => {
    if (req.method !== 'GET') {
        res.writeHead(403, { 'Content-Type': 'text/plain' });
        res.end('403 Forbidden');
        return;
    }

    const basePath = req.url.split('?')[0];  // '?' より前の部分だけを取得
    const tmpPath = path.join(__dirname, basePath === '/' ? '/home/index.html' : basePath);
    const filePath = path.normalize(tmpPath);

    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
        } else {
            const extname = path.extname(filePath);
            let contentType = 'text/html'; // デフォルトはHTML

            switch (extname) {
                case '.js':
                    contentType = 'application/javascript';
                    break;
                case '.css':
                    contentType = 'text/css';
                    break;
                case '.json':
                    contentType = 'application/json';
                    break;
                case '.jpg':
                case '.jpeg':
                    contentType = 'image/jpeg';
                    break;
                case '.png':
                    contentType = 'image/png';
                    break;
                case '.gif':
                    contentType = 'image/gif';
                    break;
                // 他の拡張子に対しても設定可能
            }

            res.writeHead(200, { 'Content-Type': contentType });

            // HTMLファイルの場合、環境変数を埋め込む
            if (extname === '.html') {
                let htmlContent = data.toString();

                // environment variables を埋め込む
                htmlContent = htmlContent.replace(
                    '<script id="load_env"></script>',
                    `<script>
                        window.env = {
                            ACCOUNT_HOST: '${accountHost}',
                            TOURNAMENT_HOST: '${tournamentHost}',
                            GAME_HOST: '${gameHost}'
                        };
                    </script>`
                );

                res.end(htmlContent);
            } else {
                // HTML以外のファイルはそのまま送信
                res.end(data);
            }
        }
    });
});

server.listen(3000, () => {
  console.log('Server running at http://localhost:3000/');
});
