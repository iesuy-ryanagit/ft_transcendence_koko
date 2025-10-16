// game.js
let gameLoopId = null;
let renderLoopId = null;
let fetchGameStateInterval = null; // サーバー取得ループ
let now_matches;
let player1_alias;
let player2_alias;
let matchId = null;
let selectedTournamentId = null;
let isGameEnded = false;
let isFetching = false;

let player1 = { x: 20, y: 100, dy: 5 };
let player2 = { x: 570, y: 100, dy: 5 };
let upPressed = false, downPressed = false, wPressed = false, sPressed = false;

let ball = { x: 300, y: 200, vx: 5, vy: 5 };
let gameState = null;
let settings = { ball_speed: 5, timer: 60 };
let lastPaddleUpdate = 0;

// -----------------------
// 入力チェック
// -----------------------
function validateInput3(input) {
    const regex = /^[a-zA-Z0-9]+$/;
    return regex.test(input);
}

// -----------------------
// ゲーム設定
// -----------------------
async function saveGameSettings() {
    const ball_speed = document.getElementById('ball-speed').value;
    const timer = 60;
    const token = localStorage.getItem('access_token');
    if (!token) { alert('ログインしてください'); return; }

    try {
        const response = await fetch(apiBase + 'setup-game/', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ ball_speed, timer })
        });

        const text = await response.text();
        try {
            const data = JSON.parse(text);
            if (response.ok) alert('設定を保存しました！');
            else alert('設定保存失敗: ' + (data.message || 'サーバーエラー'));
        } catch {
            alert('サーバーから不正なレスポンスが返されました');
        }
    } catch (error) {
        console.error(error);
        alert('通信エラーが発生しました');
    }
}

async function loadGameSettings() {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
        const response = await fetch(apiBase + 'setup-game/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('設定取得失敗');

        const data = await response.json();

        if (data.ball_speed === undefined) throw new Error('APIレスポンスに必要なデータがありません');

        const ballSpeedInput = document.getElementById('ball-speed');
        const ballSpeedValue = document.getElementById('ball-speed-value');

        if (!ballSpeedInput || !ballSpeedValue) throw new Error('HTML要素が見つかりません');

        ballSpeedInput.value = data.ball_speed;
        ballSpeedValue.textContent = data.ball_speed;

        return data;
    } catch (error) {
        console.error(error);
        alert('ゲーム設定の取得に失敗しました');
        return null;
    }
}

// -----------------------
// プレイヤー登録
// -----------------------
function registerPlayer(tournamentId) {
    selectedTournamentId = tournamentId;
    document.getElementById("playerRegisterModal").style.display = "block";
}

function closeModal() {
    document.getElementById("playerRegisterModal").style.display = "none";
}

function submitPlayerRegistration() {
    const alias = document.getElementById("playerNameInput").value;
    if (!alias || !validateInput3(alias)) {
        alert('有効なプレイヤー名を入力してください');
        return;
    }
    if (!selectedTournamentId) { alert('トーナメントが選択されていません'); return; }

    const token = localStorage.getItem('access_token');
    fetch(TournamentBase + `tournament/join/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ tournament_id: selectedTournamentId, alias })
    })
    .then(res => res.json().then(data => {
        if (!res.ok) throw new Error(data.message || '登録失敗');
        alert('プレイヤーが登録されました');
        closeModal();
    }))
    .catch(err => { alert('登録エラー: ' + err.message); });
}

// -----------------------
// キー入力
// -----------------------
document.addEventListener("keydown", e => {
    if (e.key === "ArrowUp") upPressed = true;
    if (e.key === "ArrowDown") downPressed = true;
    if (e.key === "w") wPressed = true;
    if (e.key === "s") sPressed = true;
});

document.addEventListener("keyup", e => {
    if (e.key === "ArrowUp") upPressed = false;
    if (e.key === "ArrowDown") downPressed = false;
    if (e.key === "w") wPressed = false;
    if (e.key === "s") sPressed = false;
});

// -----------------------
// 試合開始
// -----------------------
async function startMatch(_matchId, alias_one, alias_two) {
    stopGameLoop();
    gameState = null;
    isGameEnded = false;

    player1_alias = alias_one;
    player2_alias = alias_two;

    try {
        const gameSettings = await loadGameSettings();
        if (!gameSettings) throw new Error('ゲーム設定取得失敗');

        settings = { ball_speed: gameSettings.ball_speed, timer: gameSettings.timer };

        const token = localStorage.getItem('access_token');
        if (!token) throw new Error('認証トークンなし');

        const response = await fetch(GameBase + 'pong/start/', {
            method: "POST",
            headers: { 'Content-Type': 'application/json','Authorization': `Bearer ${token}`},
            body: JSON.stringify({ match_id: _matchId, ball_speed: settings.ball_speed, game_timer: settings.timer })
        });
        if (!response.ok) throw new Error('試合開始失敗');

        const data = await response.json();
        matchId = data.match_id;

        const tournamentResponse = await fetch(`${TournamentBase}tournament/${selectedTournamentId}`, {
            method: "GET",
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
        });
        if (!tournamentResponse.ok) throw new Error('トーナメント情報取得失敗');

        const tournamentData = await tournamentResponse.json();
        const targetMatch = tournamentData.matches.find(m => m.id === _matchId);
        if (!targetMatch) throw new Error('指定試合なし');

        now_matches = tournamentData.matches;
        player1_id = targetMatch.player1.id;
        player2_id = targetMatch.player2.id;

        // ボール初期化
        ball.x = 300; ball.y = 200; ball.vx = settings.ball_speed; ball.vy = settings.ball_speed;

        navigateTo("game-screen");

        isGameEnded = false;
        gameLoopId = requestAnimationFrame(gameLoop);
        renderLoopId = requestAnimationFrame(renderLoop);
        fetchGameStateInterval = setInterval(fetchGameState, 500);

    } catch (error) {
        console.error(error);
        alert('試合開始に失敗しました');
    }
}

// -----------------------
// パドル更新
// -----------------------
async function updatePaddlePosition() {
    if (!matchId) return;
    const token = localStorage.getItem('access_token');

    try {
        await fetch(`${GameBase}pong/data/`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
            body: JSON.stringify({
                match_id: matchId,
                paddles: { player1: { y: player1.y }, player2: { y: player2.y } },
                ball_speed: settings.ball_speed
            })
        });
    } catch (error) {
        console.error("パドル更新エラー:", error);
    }
}

// -----------------------
// ゲーム状態取得
// -----------------------
async function fetchGameState() {
    if (!matchId || isFetching) return;
    isFetching = true;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${GameBase}pong/data/?match_id=${matchId}`, {
            method: "GET",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        });

        if (response.ok) {
            const data = await response.json();
            gameState = { ball: data.ball, paddles: data.paddles, scores: data.scores, match_end: data.match_end };
            // サーバーとのズレ補正
            if (Math.abs(gameState.ball.x - ball.x) > 10) ball.x = gameState.ball.x;
            if (Math.abs(gameState.ball.y - ball.y) > 10) ball.y = gameState.ball.y;
        }
    } catch (error) {
        console.error(error);
    } finally {
        isFetching = false;
    }
}

// -----------------------
// ゲーム描画
// -----------------------
function drawGame() {
    if (!gameState) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.beginPath();
    ctx.arc(ball.x, ball.y, 10, 0, Math.PI*2);
    ctx.fillStyle = "red";
    ctx.fill();
    ctx.closePath();

    ctx.fillStyle = "blue";
    ctx.fillRect(player1.x, player1.y, 10, 100);
    ctx.fillStyle = "green";
    ctx.fillRect(player2.x, player2.y, 10, 100);

    document.getElementById("scoreboard").textContent =
        `${player1_alias}: ${gameState.scores.player1} | ${player2_alias}: ${gameState.scores.player2}`;

    // 試合終了処理
    if (gameState.match_end && !isGameEnded) {
        isGameEnded = true;
        const finalScore = `${gameState.scores.player1}-${gameState.scores.player2}`;
        const winnerId = gameState.scores.player1 > gameState.scores.player2 ? player1_id : player2_id;
        submitMatchResult(matchId, finalScore, winnerId);
        stopGameLoop();
    }
}

// -----------------------
// ゲームループ
// -----------------------
function gameLoop() {
    const now = Date.now();

    if (wPressed && player1.y > 0) player1.y -= player1.dy;
    if (sPressed && player1.y < canvas.height - 100) player1.y += player1.dy;
    if (upPressed && player2.y > 0) player2.y -= player2.dy;
    if (downPressed && player2.y < canvas.height - 100) player2.y += player2.dy;

    if (now - lastPaddleUpdate > 500) { updatePaddlePosition(); lastPaddleUpdate = now; }

    ball.x += ball.vx;
    ball.y += ball.vy;

    if (ball.y < 0 || ball.y > canvas.height) ball.vy *= -1;
    if (ball.x < player1.x + 10 && ball.y > player1.y && ball.y < player1.y + 100) ball.vx *= -1;
    if (ball.x > player2.x - 10 && ball.y > player2.y && ball.y < player2.y + 100) ball.vx *= -1;

    gameState = gameState || {};
    gameState.ball = { ...ball };
    gameState.paddles = { player1: { ...player1 }, player2: { ...player2 } };

    gameLoopId = requestAnimationFrame(gameLoop);
}

function renderLoop() {
    drawGame();
    renderLoopId = requestAnimationFrame(renderLoop);
}

// -----------------------
// ゲームループ停止
// -----------------------
function stopGameLoop() {
    if (gameLoopId) { cancelAnimationFrame(gameLoopId); gameLoopId = null; }
    if (renderLoopId) { cancelAnimationFrame(renderLoopId); renderLoopId = null; }
    if (fetchGameStateInterval) { clearInterval(fetchGameStateInterval); fetchGameStateInterval = null; }
    console.log("ゲームループ停止完了");
}

// -----------------------
// 状態表示補助
// -----------------------
function translateStatus(status) {
    switch(status) {
        case 'pending': return '未開始';
        case 'ongoing': return '進行中';
        case 'completed': return '完了';
        default: return '不明';
    }
}
