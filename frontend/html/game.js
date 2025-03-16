// game.js
 let gameLoopId = requestAnimationFrame(gameLoop);
 let renderLoopId = requestAnimationFrame(renderLoop);
 let fetchGameStateInterval; // ゲーム状態取得ループを制御するID
 let now_matches;
 function validateInput3(input) {
    const regex = /^[a-zA-Z0-9]+$/;
    return regex.test(input);
 }
 let player1_alias;
 let player2_alias;

 async function saveGameSettings() {
	const ball_speed = document.getElementById('ball-speed').value;
	const timer = 60;
	const token = localStorage.getItem('access_token'); // 認証トークン

	if (!token) {
		alert('認証トークンがありません。ログインし直してください。');
		return;
	}

	console.log('Sending request to:', apiBase + 'setup-game/');
	
	try {
		const response = await fetch(apiBase + 'setup-game/', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${token}`
			},
			credentials: 'include',  // 必要なら追加
			body: JSON.stringify({ball_speed, timer})
		});

		console.log('Status:', response.status);
		
		const text = await response.text();
		console.log('Response Text:', text);

		try {
			const data = JSON.parse(text); // JSONパース
			if (response.ok) {
				alert('設定を保存しました！');
			} else {
				alert('設定の保存に失敗: ' + (data.message || 'サーバーエラー'));
			}
		} catch (jsonError) {
			console.error('JSONパースエラー:', jsonError);
			alert('サーバーから不正なレスポンスが返されました。');
		}

	} catch (error) {
		console.error('設定保存中にエラー:', error);
		alert('通信エラーが発生しました');
	}
}


 async function loadGameSettings() {
	const token = localStorage.getItem('access_token'); // 認証トークン

	try {
		const response = await fetch(apiBase + 'setup-game/', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${token}`
			},
			credentials: 'include'
		});

		console.log("API Response Status:", response.status); // ステータスコードを確認

		if (!response.ok) {
			throw new Error(`設定の取得に失敗: ${response.statusText}`);
		}

		const data = await response.json();
		console.log("取得したデータ:", data); // 取得したデータを確認

		// `ballSpeed` や `timer` が存在しない場合のエラーチェック
		if (!data || data.ball_speed === undefined) {
			console.log(data.ball_speed)
			throw new Error("APIレスポンスに必要なデータがありません");
		}

		// HTML要素の取得
		const ballSpeedInput = document.getElementById('ball-speed');
		const ballSpeedValue = document.getElementById('ball-speed-value');

		if (!ballSpeedInput || !ballSpeedValue) {
			throw new Error("HTML要素が見つかりません");
		}

		// 取得したデータをUIに反映
		ballSpeedInput.value = data.ballSpeed;
		ballSpeedValue.textContent = data.ballSpeed;

		console.log("ゲーム設定を更新しました");
		return data; // 取得したデータを返す
	} catch (error) {
		console.error('設定の取得エラー:', error);
		alert('ゲーム設定の取得に失敗しました');
		return null;
	}
}

 async function viewMatches(tournamentId) {
	try {
		const token = localStorage.getItem('access_token');

		const response = await fetch(`${TournamentBase}tournament/${tournamentId}`, {
			method: 'GET',
			headers: {
				'Authorization': `Bearer ${token}`,
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			throw new Error('試合一覧の取得に失敗しました');
		}

		const data = await response.json();
		console.log('試合一覧:', data);

		// 例: 試合データを描画
		displayMatches(data.matches);
		navigateTo('match-list-page'); // 試合一覧ページに遷移する場合

	} catch (error) {
		console.error('試合詳細取得エラー:', error);
		alert('試合詳細の取得に失敗しました');
	}
}

// モーダルを開く
 function registerPlayer(tournamentId) {
	selectedTournamentId = tournamentId;
	console.log(selectedTournamentId);
	document.getElementById("playerRegisterModal").style.display = "block";
}

// モーダルを閉じる
 function closeModal() {
	document.getElementById("playerRegisterModal").style.display = "none";
}

function submitPlayerRegistration() {
	alias = document.getElementById("playerNameInput").value;
    if (!validateInput3(alias)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
	if (!alias) {
		alert("プレイヤー名を入力してください");
		return;
	}

	if (!selectedTournamentId) {
		alert("トーナメントが選択されていません。");
		return;
	}

	fetch(TournamentBase + `tournament/join/`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ tournament_id: selectedTournamentId, alias })
	})
	.then(response => {
		if (!response.ok) {
			// JSONに変換してからエラーメッセージ抽出
			return response.json().then(errData => {
				throw new Error(errData.message || '登録に失敗しました');
			});
		}
		// OKだった場合
		return response.json();
	})
	.then(data => {
		console.log(data);
		alert("プレイヤーが登録されました！");
		closeModal();  // 登録後にモーダルを閉じる
	})
	.catch(error => {
		console.error("登録エラー:", error);
		alert("登録に失敗しました: " + error.message);
	});
}


// ゲーム開始 (APIから状態を取得して描画)
// キー入力のリスニング
document.addEventListener("keydown", (event) => {
	if (event.key === "ArrowUp") {
		upPressed = true;
	}
	if (event.key === "ArrowDown") {
		downPressed = true;
	}
	if (event.key === "w") {
		wPressed = true;
	}
	if (event.key === "s") {
		sPressed = true;
	}
});

document.addEventListener("keyup", (event) => {
	if (event.key === "ArrowUp") {
		upPressed = false;
	}
	if (event.key === "ArrowDown") {
		downPressed = false;
	}
	if (event.key === "w") {
		wPressed = false;
	}
	if (event.key === "s") {
		sPressed = false;
	}
});


// ゲーム開始処理	
 async function startMatch(_matchId, alias_one, alias_two) {
	stopGameLoop(); 
    gameState = null; // 新しい試合用に初期化
    isGameEnded = false; // フラグもリセット
	player1_alias = alias_one;
	player2_alias = alias_two;
try {
	const gameSettings = await loadGameSettings();
	if (!gameSettings) throw new Error("ゲーム設定の取得に失敗しました。");

	settings = {
		ball_speed: gameSettings.ball_speed,
		timer: gameSettings.timer
	};
	console.log("ゲーム設定:", settings);

	const response = await fetch(GameBase + 'pong/start/', {
		method: "POST",
		headers: { 'Content-Type': 'application/json' },
		credentials: 'include',
		body: JSON.stringify({
			match_id: _matchId,
			ball_speed: gameSettings.ball_speed,
			game_timer: gameSettings.timer
		})
	});
	if (!response.ok) throw new Error(`試合開始に失敗しました: ${response.statusText}`);
	
	const data = await response.json();
	matchId = data.match_id;
	console.log(`試合ID: ${matchId}`);

	const tournamentResponse = await fetch(`${TournamentBase}tournament/${selectedTournamentId}`, {
		method: "GET",
		headers: { 'Content-Type': 'application/json' }
	});
	if (!tournamentResponse.ok) throw new Error(`トーナメント情報の取得に失敗: ${tournamentResponse.statusText}`);
	
	const tournamentData = await tournamentResponse.json();
	const targetMatch = tournamentData.matches.find(m => m.id === _matchId);
	if (!targetMatch) throw new Error('指定した試合が見つかりません');

	player1_id = targetMatch.player1.id;
	player2_id = targetMatch.player2.id;
	now_matches = tournamentData.matches;
	console.log(`Player1 ID: ${player1_id}, Player2 ID: ${player2_id}`);

	navigateTo("game-screen");

	isGameEnded = false; // 試合中フラグON
	gameLoopId = requestAnimationFrame(gameLoop);
	renderLoopId = requestAnimationFrame(renderLoop);
	fetchGameStateInterval = setInterval(fetchGameState, 200);

} catch (error) {
	console.error("試合開始エラー:", error);
	alert("試合開始に失敗しました。");
}
}


// パドルの位置をAPIに送信
async function updatePaddlePosition() {
	if (!matchId) return;

	// プレイヤー1（W / S キーで操作）
	if (wPressed && player1.y > 0) {
		player1.y -= player1.dy;
	}
	if (sPressed && player1.y < canvas.height - 100) {
		player1.y += player1.dy;
	}

	// プレイヤー2（↑ / ↓ キーで操作）
	if (upPressed && player2.y > 0) {
		player2.y -= player2.dy;
	}
	if (downPressed && player2.y < canvas.height - 100) {
		player2.y += player2.dy;
	}

	// API にパドルの新しい位置を送信
	try {
		const response = await fetch(`${GameBase}pong/data/`, {
			method: "PATCH",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				match_id: matchId,
				paddles: {
					player1: { y: player1.y },
					player2: { y: player2.y },
				},
				ball_speed: settings.ball_speed
			})
		});

		if (!response.ok) {
			throw new Error(`パドル位置の更新に失敗: ${response.statusText}`);
		}

	} catch (error) {
		console.error("パドル位置更新エラー:", error);
	}
}


// 最新のゲーム状態を取得
async function fetchGameState() {
    if (!matchId || isFetching) return;
    isFetching = true;

    try {
        const response = await fetch(`${GameBase}pong/data/?match_id=${matchId}`, {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });

        if (response.ok) {
            const data = await response.json();
            gameState = {
                ball: data.ball,
                scores: data.scores,
                paddles: data.paddles,
                match_end: data.match_end
            };
        }
    } catch (error) {
        console.error("ゲーム状態の取得エラー:", error);
    } finally {
        isFetching = false;
    }
}

// ゲーム画面の描画
function drawGame() {
	if (!gameState) return;

	ctx.clearRect(0, 0, canvas.width, canvas.height);

	// ボール描画
	ctx.beginPath();
	ctx.arc(gameState.ball.x, gameState.ball.y, 10, 0, Math.PI * 2);
	ctx.fillStyle = "red";
	ctx.fill();
	ctx.closePath();

	// プレイヤー1パドル描画
	ctx.fillStyle = "blue";
	ctx.fillRect(gameState.paddles.player1.x, gameState.paddles.player1.y, 10, 100);

	// プレイヤー2パドル描画
	ctx.fillStyle = "green";
	ctx.fillRect(gameState.paddles.player2.x, gameState.paddles.player2.y, 10, 100);

	// スコア表示更新
	document.getElementById("scoreboard").textContent =
		`${player1_alias}: ${gameState.scores.player1} | ${player2_alias}: ${gameState.scores.player2}`;

	// 試合終了処理 (一度だけ実行)
	// drawGame内の試合終了処理
	if (gameState.match_end && !isGameEnded) {
		console.log("試合終了処理開始");

		isGameEnded = true; // 一度だけ実行

		// スコア計算例: "5-1"
		const finalScore = `${gameState.scores.player1}-${gameState.scores.player2}`;

		// 勝者判定
		let winnerId = gameState.scores.player1 > gameState.scores.player2 ? player1_id : player2_id;

		// API送信
		submitMatchResult(matchId, finalScore, winnerId);

		// ループ停止
		stopGameLoop();
	}

}

function gameLoop() {
	updatePaddlePosition();  // キー入力を反映
	gameLoopId = requestAnimationFrame(gameLoop);  // 次のフレームを描画
}

function renderLoop() {
	drawGame();  // 常に最新の gameState を描画
	renderLoopId = requestAnimationFrame(renderLoop);  // 次のフレームを描画
}


async function submitMatchResult(matchId, finalScore, winnerId) {
	const body = {
		match_id: String(matchId),         // 必ず文字列として
		final_score: String(finalScore),   // 必ず文字列として ("5-1")
		winner: Number(winnerId)           // 数値として
	};

	console.log("送信データ:", body); // 確認用ログ

	try {
		// ① 試合結果送信
		const response = await fetch(`${TournamentBase}tournament/match/end/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(body)
		});

		const responseText = await response.text(); // レスポンス確認用
		console.log("サーバーレスポンス:", responseText);

		if (!response.ok) {
			console.error("エラー詳細:", responseText);
			throw new Error(`試合結果送信失敗: ${response.statusText}`);
		}

		const data = JSON.parse(responseText);

		// ② next_round が pending なら試合リスト取得
		if (data.next_round && data.next_round.status === 'next_round_pending') {
			console.log('次ラウンド保留中: 最新試合一覧を取得します');

			// トーナメントIDを取得 (事前に定義されていることが前提)
			const tournamentId = selectedTournamentId; // 例えばグローバル変数から参照

			if (!tournamentId) {
				console.error("トーナメントIDが未設定です。");
				return;
			}

			// ③ トーナメント試合リストAPI呼び出し
			const matchesResponse = await fetch(`${TournamentBase}tournament/${tournamentId}/`, {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' }
			});

			if (!matchesResponse.ok) {
				throw new Error(`試合リストの取得失敗: ${matchesResponse.statusText}`);
			}

			const matchesData = await matchesResponse.json();
			console.log('最新の試合データ:', matchesData);

			// ④ 試合リスト表示
			displayMatches(matchesData.matches); // displayMatches関数へ渡す
			navigateTo('match-list-page'); // 試合一覧画面へ遷移
		}
		else if (data.next_round.status == 'goto_nextround')
		{
			displayMatches(data.next_round.matches);
			navigateTo('match-list-page');
		}
		else if (data.next_round.status == 'tournament_completed')
		{
			//勝利者がどっちかを表示してもいいかも？
			enableNavigation(true);
			navigateTo('dashboard');
		}

		// 必要であれば "試合結果送信成功" のメッセージ
		alert('試合結果が送信されました！');

	} catch (error) {
		console.error('試合結果送信エラー:', error);
		alert('試合結果の送信に失敗しました。');
	}
}


async function startTournament(tournamentId) {
if (!tournamentId) {
	alert('トーナメントIDが指定されていません');
	return;
}

const token = localStorage.getItem('access_token');
if (!token) {
	alert('ログインしてください');
	return;
}

try {
	const response = await fetch(`${TournamentBase}tournament/start/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ tournament_id: tournamentId })
	});

	const data = await response.json(); // 先にJSONを読む（エラーでも読めるように)	
	if (!response.ok) {
		console.error('サーバーからのエラー:', data);
		alert('試合開始失敗: ' + (data.message || '不明なエラー'));
		return;
	}

	console.log('試合データ:', data.matches);
	selectedTournamentId = tournamentId;
	displayMatches(data.matches);
	navigateTo('match-list-page');

} catch (error) {
	console.error('試合開始エラー:', error);
	alert('通信エラー: ' + error.message);
}
}

// 試合リスト表示
function displayMatches(matches) {
	enableNavigation(false);
	const container = document.getElementById('match-list-container');
	container.innerHTML = '';

	if (matches.length === 0) {
		container.innerHTML = '<p>試合が見つかりません。</p>';
		return;
	}

	matches.forEach(match => {
	const item = document.createElement('div');
	item.className = 'list-group-item d-flex justify-content-between align-items-center';

	// 状態に応じてボタン切り替え
	let actionButton = '';
	if (match.status === 'pending') {
		// 試合開始ボタン（クリック可能）
		actionButton = `<button class="btn btn-primary" onclick="startMatch('${match.id}', '${match.player1.alias}', '${match.player2.alias}')">試合開始</button>`;
	} else if (match.status === 'ongoing') {
		// 試合中表示（クリック不可）
		actionButton = `<button class="btn btn-warning" disabled>試合中</button>`;
	} else if (match.status === 'completed') {
		// 完了している場合の表示（任意で詳細ボタン等も可能）
		actionButton = `<button class="btn btn-success" disabled>完了</button>`;
	}

	item.innerHTML = `
		<span><strong>${match.player1.alias}</strong> vs <strong>${match.player2.alias}</strong></span>
		<div>
			<span class="badge bg-secondary me-2">${translateStatus(match.status)}</span>
			${actionButton}
		</div>
	`;
	container.appendChild(item);
});
}

function stopGameLoop() {
    if (gameLoopId) {
        cancelAnimationFrame(gameLoopId);
        gameLoopId = null;
    }
    if (renderLoopId) {
        cancelAnimationFrame(renderLoopId);
        renderLoopId = null;
    }
    if (fetchGameStateInterval) {
        clearInterval(fetchGameStateInterval);
        fetchGameStateInterval = null;
    }
    console.log("ゲームループ停止完了");
}


// 状態を日本語に変換する関数（オプション）
function translateStatus(status) {
switch (status) {
	case 'pending':
		return '未開始';
	case 'ongoing':
		return '進行中';
	case 'completed':
		return '完了';
	default:
		return '不明';
}
}

