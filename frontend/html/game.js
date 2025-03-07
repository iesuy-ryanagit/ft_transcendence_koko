const apiBase = "http://localhost:8001/api/";

// 試合を開始し、ゲーム画面に移動
async function startTournament(tournamentId) {
    try {
        const response = await fetch(`${apiBase}pong/start/${tournamentId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("試合開始APIエラー");
        }

        const data = await response.json();
        console.log("試合開始:", data);

        // ゲーム画面に遷移
        navigateTo("game-screen");
        startGame(tournamentId);

    } catch (error) {
        console.error("試合開始エラー:", error);
        alert("試合を開始できませんでした");
    }
}

// ゲーム開始 (APIから状態を取得して描画)
async function startGame(tournamentId) {
    let gameState = null;
    const canvas = document.getElementById("pongCanvas");
    const ctx = canvas.getContext("2d");

    async function fetchGameState() {
        try {
            const response = await fetch(`${apiBase}pong/state/${tournamentId}`);
            if (!response.ok) throw new Error("ゲーム状態取得エラー");

            const data = await response.json();
            gameState = data.state;
            drawGame();

        } catch (error) {
            console.error("ゲーム状態取得エラー:", error);
        }
    }

    function drawGame() {
        if (!gameState) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ボール描画
        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(gameState.ball.x, gameState.ball.y, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.closePath();

        // パドル描画
        ctx.fillStyle = "blue";
        ctx.fillRect(gameState.paddles.player1.x, gameState.paddles.player1.y, 10, 100);
        ctx.fillStyle = "green";
        ctx.fillRect(gameState.paddles.player2.x, gameState.paddles.player2.y, 10, 100);

        // スコア表示
        document.getElementById("scoreboard").innerText =
            `Player 1: ${gameState.scores.player1} | Player 2: ${gameState.scores.player2}`;
    }

    // 1秒ごとにゲーム状態を更新
    setInterval(fetchGameState, 1000);
}

// 画面遷移関数 (既存)
function navigateTo(page) {
    document.querySelectorAll(".page").forEach(p => p.classList.add("d-none"));
    document.getElementById(page).classList.remove("d-none");
}
