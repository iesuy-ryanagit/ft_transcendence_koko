	const apiBase = 'http://localhost:8000/api/';
	const TournamentBase = 'http://localhost:8002/api/';
	const GameBase = 'http://localhost:8001/api/';
	let selectedTournamentId = null; 

	let matchId = null;
	let gameState = null;

	const canvas = document.getElementById("pongCanvas");
	const ctx = canvas.getContext("2d");

	const player1 = { y: 150, dy: 10 };
	const player2 = { y: 150, dy: 10 };

	let upPressed = false;
	let downPressed = false;
	let wPressed = false;  // ← 追加
	let sPressed = false;  // ← 追加
	let isFetching = false;

	$(window).on("popstate", function (event) {
		let page = location.hash.replace('#', '');
		if (!page || !document.getElementById(page)) {
			page = 'loginSelection'; // 存在しないページなら loginSelection にする
		}
	
		if (page === 'tournament-list') {
			loadTournamentList();
		}
		console.log('Popstate triggered, navigating to:', page);
	
		navigateTo(page, false);
	});
	
	


	async function login() {
		const username = document.getElementById('login-username').value;
		const password = document.getElementById('login-password').value;

		const response = await fetch(apiBase + 'login/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			credentials: 'include',
			body: JSON.stringify({ username, password })
		});

		const data = await response.json();
		if (response.ok) {
			localStorage.setItem('access_token', data.jwt);
			localStorage.setItem('username', username);
			document.cookie = `jwt=${data.jwt}; path=/; max-age=86400; SameSite=Lax`;
			await fetchUserProfile();
			enableNavigation(true);
			navigateTo('dashboard');
		} else {
			alert('ログイン失敗: ' + (data.message || 'サーバーエラー'));
		}
	}

	async function fetchUserProfile() {
		const token = localStorage.getItem('access_token');
		if (!token) {
			console.warn('アクセストークンがありません');
			return;
		}

		try {
			const response = await fetch(apiBase + 'profile/', {
				method: 'GET',
				headers: { 'Authorization': `Bearer ${token}` },
				credentials: 'include'
			});

			const data = await response.json();
			if (!response.ok) {
				throw new Error(data.message || 'プロフィール取得に失敗しました');
			}

			// プロフィール情報を保存
			localStorage.setItem('username', data.username);
			localStorage.setItem('email', data.email);
			localStorage.setItem('opt', data.otp_enabled);

			console.log('プロフィール情報:', data);

		} catch (error) {
			console.error('プロフィール取得エラー:', error);
		}
	}

	async function loginWith2FA() {
		const username = document.getElementById('tfalogin-username').value;
		const password = document.getElementById('tfalogin-password').value;
		const otp = document.getElementById('tfalogin-token').value;

		const response = await fetch(apiBase + 'login-tfa/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			credentials: 'include',
			body: JSON.stringify({ username, password, otp })
		});

		const data = await response.json();
		if (response.ok) {
			localStorage.setItem('access_token', data.jwt);
			localStorage.setItem('username', username);
			document.cookie = `jwt=${data.jwt}; path=/; max-age=86400; SameSite=Lax`;
			await fetchUserProfile();
			enableNavigation(true);
			navigateTo('dashboard');
		} else {
			alert('2FAログイン失敗: ' + (data.detail || 'サーバーエラー'));
		}
	}

	//外部リンクへ飛ぶ
	async function Goto42Oauth() {
		try {
			// FetchでURLを取得
			const response = await fetch(apiBase + 'oauth/url42/', {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
			});
			// レスポンスが正常かどうかをチェック
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}

			// レスポンスをJSONとしてパース
			const data = await response.json();

			// 取得したURLでリダイレクト
			if (data && data.oauth_url) {
				window.location.href = data.oauth_url; // レスポンスのURLにリダイレクト
			} else {
				console.error('URL not found in response');
			}

		} catch (error) {
			// エラー時にエラーメッセージを表示
			alert('リダイレクト失敗: ' + error.message || 'サーバーエラー');
		}
	}


	//外部リンクから取得したcodeでログインする
	async function loginWith42Oauth() {
		const urlParams = new URLSearchParams(window.location.search);
		const code = urlParams.get('code');  // 'code'を変数に格納

		if (code) {
			try {
				const response = await fetch(apiBase + 'oauth/login42/', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					credentials: 'include',
					body: JSON.stringify({ code })  // codeをJSONで送信
				});

				// レスポンスが正常かどうかを確認
				if (!response.ok) {
					throw new Error(`Failed to login: ${response.statusText}`);
				}

				const data = await response.json();  // JSON形式でレスポンスを取得

				// JWTの保存（セキュリティ考慮）
				if (data.jwt) {
					localStorage.setItem('access_token', data.jwt);
					document.cookie = `jwt=${data.jwt}; path=/; max-age=86400; Secure; SameSite=Lax`; // セキュアなクッキーに保存
				} else {
					throw new Error('JWT not found in the response');
				}

				// ユーザープロフィールを取得し、ナビゲーションを有効化
				await fetchUserProfile();
				enableNavigation(true);

				// ダッシュボードに遷移
				navigateTo('dashboard');
			} catch (error) {
				// エラーハンドリング
				console.error('Error during login or signup:', error.message);
				alert('ログインに失敗しました。再度お試しください。');
			}
		} else {
			console.error('No code found in the URL');
			alert('認証に必要なcodeがURLに含まれていません。');
		}
	}



	// サインアップ処理
	async function signUp() {
		const username = document.getElementById('signup-username').value;
		const password = document.getElementById('signup-password').value;

		const response = await fetch(apiBase + 'signup/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ username, password })
		});

		const data = await response.json();
		if (response.ok) {
			showLogin(true);
		} else {
			alert('登録失敗: ' + data.message);
		}
	}




	// セットアップ2FA処理
	async function setUpTfa() {

		const response = await fetch(apiBase + 'setup-tfa/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			credentials: 'include'  // 必要なら追加
		});

		const data = await response.json();
		if (response.ok) {
			alert('セットアップ成功!');
		} else {
			alert('セットアップ失敗: ' + data.message);
		}
	}

	function enableNavigation(enable) {
		document.getElementById('nav-dashboard').classList.toggle('disabled', !enable);;
		document.getElementById('nav-logout').classList.toggle('disabled', !enable);
		document.getElementById('nav-tfasign').classList.toggle('disabled', !enable);
	}

	// 画面遷移関数
	function navigateTo(page, addHistory = true) {
		console.log("Navigating to:", page);
	
		if (!document.getElementById(page)) {
			console.error(`Page not found: ${page}`);
			return;
		}
	
		if (location.hash === `#${page}`) {
			console.log("Same page, skipping pushState");
			return;
		}
	
		document.querySelectorAll('.page').forEach(p => p.classList.add('d-none'));
	
		document.getElementById(page).classList.remove('d-none');
		console.log(`Showing page: ${page}`);
	
		// 🔹 ここでトーナメントリストをロード
		if (page === 'tournament-list') {
			console.log("Loading tournament list...");
			loadTournamentList();
		}
	
		if (addHistory) {
			history.pushState({ page }, '', `#${page}`);
		}
	}
	
	
	

	async function fetchTournaments() {
		const token = localStorage.getItem('access_token');

		const response = await fetch(TournamentBase + 'tournament/list/', {
			method: 'GET',
			headers: { 'Authorization': 'Bearer ' + token }
		});

		const data = await response.json();

		if (response.ok) {
			const list = document.getElementById('tournament-list');
			list.innerHTML = '';
			data.forEach(tournament => {
				const item = document.createElement('a');
				item.className = 'list-group-item list-group-item-action';
				item.textContent = tournament.name;
				item.href = '#';
				item.onclick = () => showMatchResult(tournament.id);
				list.appendChild(item);
			});
		} else {
			alert('トーナメント一覧取得失敗');
		}
	}

	async function createTournament() {
		const name = document.getElementById('tournament-name').value;
		const max_participants = document.getElementById('tournament-size').value;
		const token = localStorage.getItem('access_token');

		const response = await fetch(TournamentBase + 'tournament/create/', {
			method: 'POST',
			headers: { 
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + token
			},
			body: JSON.stringify({name, max_participants})

		});

		const data = await response.json();

		if (response.ok) {
			navigateTo('dashboard');
		} else {
			alert('作成失敗: ' + (data.message || 'サーバーエラー'));
		}
	}

	async function fetchTFAQRCode() {
		const token = localStorage.getItem('access_token'); // ログイン時に保存したJWTトークン

		if (!token) {
			alert("ログインが必要です");
			return;
		}

		try {
			const response = await fetch(apiBase + 'setup-tfa/', {
				method: "GET",
				headers: {
					"Authorization": `Bearer ${token}`, // 認証ヘッダーにJWTトークンを設定
					"Content-Type": "application/json"
				},
				credentials: 'include',
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.message || "2FAのQRコード取得に失敗しました");
			}

			const data = await response.json();
			console.log("APIレスポンス:", data);
			displayQRCode(data.qr_url, data.secret_key);

		} catch (error) {
			alert(`エラー: ${error.message}`);
		}
	}

	async function sendTFAExitRequest() {
		const token = localStorage.getItem("access_token");
		if (!token) {
			console.warn("アクセストークンがありません。");
			return;
		}

		try {
			console.log("2FA終了リクエスト送信中...");

			const response = await fetch(apiBase + 'signup-tfa/',  {
				method: "POST",
				headers: {
					"Authorization": `Bearer ${token}`,
					"Content-Type": "application/json"
				},
				credentials: 'include',  // 必要なら追加
				body: JSON.stringify({ action: "exit_2fa" }) 
			});

			console.log("APIレスポンス:", response);

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.message || "APIリクエストに失敗しました");
			}

			console.log("2FA終了リクエスト送信成功");
		} catch (error) {
			console.error("エラー:", error);
		}
	}


	// 画面切り替え関数
	function showLogin(addHistory = true) {
		navigateTo('login', addHistory);
	}

	function showLoginSelect(addHistory = true){
		navigateTo('loginSelection', addHistory);
	}

	function showSignUp(addHistory = true) {
		navigateTo('signup', addHistory);
	}

	function showDashboard(addHistory = true) {
		navigateTo('dashboard', addHistory);
	}

	function showCreateTournament(addHistory = true) {
		navigateTo('create-tournament', addHistory);
	}

	function showMatchResult(addHistory = true) {
		navigateTo('match-result', addHistory);
	}

	function showGameSettings(addHistory = true) {
		navigateTo('game-settings', addHistory);
	}

	function showTournamentManegement(addHistory = true) {
		navigateTo('tournament-management', addHistory);
	}

	function showTournamentList(addHistory = true) {
		navigateTo('tournament-list', addHistory);
	}

	async function showTFARegister(addHistory = true) {
		await fetchTFAQRCode(); // QRコード取得を待つ
		navigateTo('TFAregister', addHistory);

		// 2FA登録画面が表示されたらボタンを取得
		const observer = new MutationObserver((mutations, obs) => {
			const backButton = document.querySelector("#TFAregister .btn-secondary");
			if (backButton && !document.getElementById('TFAregister').classList.contains('d-none')) {
				console.log("戻るボタンが見つかりました");
				backButton.addEventListener("click", async function () {
					console.log("戻るボタンクリック: 2FA終了リクエストを送信");
					await sendTFAExitRequest();
					navigateTo("dashboard");
				});
				obs.disconnect(); // イベント登録後に監視を停止
			}
		});

		observer.observe(document.getElementById('TFAregister'), { attributes: true, attributeFilter: ['class'] });
	}


	function displayQRCode(otpAuthUrl, secretKey) {
		console.log("OTP Auth URL:", otpAuthUrl); // デバッグ用
		
		document.getElementById("tfa-secret-key").textContent = secretKey;
		document.getElementById("TFAregister").classList.remove("d-none");

		const qrContainer = document.getElementById("tfa-qr-image");

		// 前のQRコードを削除
		qrContainer.innerHTML = "";

		// QRコードを生成
		new QRCode(qrContainer, {
			text: otpAuthUrl,
			width: 200,
			height: 200
		});
	}


	// ログアウト処理
	function logout() {
		console.log("ログアウト処理開始");
	
		// ローカルストレージ削除
		localStorage.clear();
		console.log("localStorage 全削除");
	
		// ナビゲーション無効化
		enableNavigation(false);
		console.log("ナビゲーション無効化");
	
		// `history.pushState()` をクリアして `popstate` が発火しないようにする
		history.pushState(null, '', location.pathname);  // これで `hash` をリセット
	
		// `history.replaceState()` を使用して履歴を書き換え
		history.replaceState({}, '', '#loginSelection');
		console.log("履歴を置換: loginSelection");
	
		// 画面を遷移
		navigateTo('loginSelection', false);
	}
	
	
	// ページ読み込み時の処理（URLの `#` を元に復元）
	document.addEventListener('DOMContentLoaded', () => {
		const canvas = document.getElementById("pongCanvas");
		const ctx = canvas.getContext("2d");
	
		if (!canvas || !ctx) {
			console.error("Canvasが取得できませんでした");
			return;
		}
		const backButton = document.querySelector("#TFAregister .btn-secondary");
		
		if (backButton) {
			backButton.addEventListener("click", async function () {
				await sendTFAExitRequest();
				navigateTo("dashboard");
			});
		}

		// スライダーの値を表示に反映
		const ballSpeedSlider = document.getElementById('ball-speed');
		const ballSpeedValue = document.getElementById('ball-speed-value');
		
		if (ballSpeedSlider && ballSpeedValue) {
			ballSpeedSlider.addEventListener('input', function () {
				ballSpeedValue.textContent = this.value;
			});
		}

		// ページ読み込み時にゲーム設定をロード
		if (document.getElementById('game-settings')) {
			loadGameSettings();
		}

		const token = localStorage.getItem('access_token');
		enableNavigation(!!token);

		// 初回ロード時にURLの `#` に応じて画面を表示
		const page = location.hash.replace('#', '') || 'loginSelection';
		navigateTo(token ? page : 'loginSelection', false);
	});


	async function saveGameSettings() {
		const ball_speed = document.getElementById('ball-speed').value;
		const timer = document.getElementById('match-duration').value;
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
			if (!data || data.ball_speed === undefined || data.timer === undefined) {
				console.log(data.ball_speed)
				console.log(data.timer)
				throw new Error("APIレスポンスに必要なデータがありません");
			}
	
			// HTML要素の取得
			const ballSpeedInput = document.getElementById('ball-speed');
			const ballSpeedValue = document.getElementById('ball-speed-value');
			const matchDuration = document.getElementById('match-duration');
	
			if (!ballSpeedInput || !ballSpeedValue || !matchDuration) {
				throw new Error("HTML要素が見つかりません");
			}
	
			// 取得したデータをUIに反映
			ballSpeedInput.value = data.ballSpeed;
			ballSpeedValue.textContent = data.ballSpeed;
			matchDuration.value = data.timer;
	
			console.log("ゲーム設定を更新しました");
			return data; // 取得したデータを返す
		} catch (error) {
			console.error('設定の取得エラー:', error);
			alert('ゲーム設定の取得に失敗しました');
			return null;
		}
	}
	

	function loadTournamentList() {
		const container = document.getElementById("tournament-list-container");
		container.innerHTML = "<p>読み込み中...</p>";

		fetch(TournamentBase + 'tournament/list')
			.then(response => response.json())
			.then(data => {
				console.log(data);
				if (data.length === 0) {
					container.innerHTML = "<p>トーナメントがありません。</p>";
					return;
				}
				container.innerHTML = data.map(tournament => `
					<div class="card my-2">
						<div class="card-body">
							<h5 class="card-title">${tournament.name}</h5>
							<p class="card-text">最大参加可能人数: ${tournament.max_participants}</p>
							<button class="btn btn-success" onclick="registerPlayer('${tournament.id}')">プレイヤー登録</button>
							<button class="btn btn-warning" onclick="startTournament('${tournament.id}')">試合開始</button>
						</div>
					</div>
				`).join("");
			})
			.catch(error => {
				console.error("トーナメント一覧の取得に失敗:", error);
				container.innerHTML = "<p>データを取得できませんでした。</p>";
			});
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
		const alias = document.getElementById("playerNameInput").value;
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
		.then(response => response.json())
		.then(data => {
			alert("プレイヤーが登録されました！");
			closeModal();  // 登録後にモーダルを閉じる
		})
		.catch(error => {
			console.error("登録エラー:", error);
			alert("登録に失敗しました");
		});
	}
	
	// ゲーム開始 (APIから状態を取得して描画)
// キー入力のリスニング
document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowUp") {
        upPressed = true;
        console.log("ArrowUp Pressed");
    }
    if (event.key === "ArrowDown") {
        downPressed = true;
        console.log("ArrowDown Pressed");
    }
    if (event.key === "w") {
        wPressed = true;
        console.log("W Pressed");
    }
    if (event.key === "s") {
        sPressed = true;
        console.log("S Pressed");
    }
});

document.addEventListener("keyup", (event) => {
    if (event.key === "ArrowUp") {
        upPressed = false;
        console.log("ArrowUp Released");
    }
    if (event.key === "ArrowDown") {
        downPressed = false;
        console.log("ArrowDown Released");
    }
    if (event.key === "w") {
        wPressed = false;
        console.log("W Released");
    }
    if (event.key === "s") {
        sPressed = false;
        console.log("S Released");
    }
});


// ゲーム開始処理
async function startTournament(tournamentId) {
    try {
        // ゲーム設定を取得
        const gameSettings = await loadGameSettings();
        if (!gameSettings) {
            throw new Error("ゲーム設定の取得に失敗しました。");
        }

		const settings = {
			ball_speed: gameSettings.ball_speed,
			timer: gameSettings.timer
		}
		console.log(settings)
        // APIリクエスト送信
        const response = await fetch(GameBase + 'pong/start/', {
            method: "POST",
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
            body: JSON.stringify({
                match_id: tournamentId,
				settings
            })
        });

        if (!response.ok) {
            throw new Error(`試合開始に失敗しました: ${response.statusText}`);
        }

        const data = await response.json();
        matchId = data.match_id;
        console.log(`試合ID: ${matchId}`);

        navigateTo("game-screen");

        setTimeout(() => {
            fetchGameState();  // 初回の状態を取得
            setInterval(fetchGameState, 500);  // 500msごとにゲーム状態を更新
            setInterval(updatePaddlePosition, 100);  // 100msごとにパドルの位置を更新
        }, 1000);
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

    console.log(`Player1 Y: ${player1.y}, Player2 Y: ${player2.y}`);

    // API にパドルの新しい位置を送信
    try {
        const response = await fetch(`${GameBase}pong/data/`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                match_id: matchId,
                paddles: {
                    player1: { y: player1.y },
                    player2: { y: player2.y }
                }
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
    if (!matchId || isFetching) return;  // すでにリクエスト中ならスキップ
    isFetching = true;  // リクエスト開始

    try {
        const response = await fetch(`${GameBase}pong/data/?match_id=${matchId}`, {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
            throw new Error(`ゲーム状態の取得に失敗: ${response.statusText}`);
        }

        const data = await response.json();
        gameState = data;
        drawGame();
    } catch (error) {
        console.error("ゲーム状態の取得エラー:", error);
    } finally {
        isFetching = false;  // リクエスト終了
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

    // プレイヤー1パドル描画（最新の gameState を使用）
    ctx.fillStyle = "blue";
    ctx.fillRect(gameState.paddles.player1.x, gameState.paddles.player1.y, 10, 100);

    // プレイヤー2パドル描画（最新の gameState を使用）
    ctx.fillStyle = "green";
    ctx.fillRect(gameState.paddles.player2.x, gameState.paddles.player2.y, 10, 100);

    // スコア表示更新
    document.getElementById("scoreboard").textContent = 
        `Player 1: ${gameState.scores.player1} | Player 2: ${gameState.scores.player2}`;

    // 試合終了処理
    if (gameState.match_end) {
        alert("試合終了！");
        navigateTo("dashboard");
    }
}

function gameLoop() {
    updatePaddlePosition();  // キー入力を反映
    requestAnimationFrame(gameLoop);  // 次のフレームを描画
}

// ゲーム開始時に gameLoop を呼び出す
requestAnimationFrame(gameLoop);

function renderLoop() {
    drawGame();  // 常に最新の gameState を描画
    requestAnimationFrame(renderLoop);  // 次のフレームを描画
}

// ゲーム開始時に renderLoop を呼び出す
requestAnimationFrame(renderLoop);


// 100ms に変更して負荷を軽減
setInterval(fetchGameState, 100);