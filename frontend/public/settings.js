// gameVariables.js

 const apiBase = window.env.ACCOUNT_HOST;
 const TournamentBase = window.env.TOURNAMENT_HOST;
 const GameBase = window.env.GAME_HOST;

 let selectedTournamentId = null;

 let matchId = null;
 let gameState = null;

 const canvas = document.getElementById("pongCanvas");
 const ctx = canvas.getContext("2d");

 const player1 = { y: 150, dy: 10 };
 const player2 = { y: 150, dy: 10 };

 let upPressed = false;
 let downPressed = false;
 let wPressed = false;
 let sPressed = false;
 let isFetching = false;
 let alias;
 let player1_id;
let player2_id;

let isGameEnded = false; // 試合が終了したかどうか

	$(window).on("popstate", function (event) {
		stopGameLoop();
    	// token is no longer available in JS when using httpOnly cookie
    	const username = localStorage.getItem("username");
        if (username)
            enableNavigation(true);
		let page = location.hash.replace('#', '');
		if (!page || !document.getElementById(page)) {
			page = 'loginSelection'; // 存在しないページなら loginSelection にする
		}
	
		if (page === 'tournament-list') {
			loadTournamentList();
		}
	
		navigateTo(page, false);
	});

	 function enableNavigation(enable) {
		document.getElementById('nav-dashboard').classList.toggle('disabled', !enable);;
		document.getElementById('nav-logout').classList.toggle('disabled', !enable);
		document.getElementById('nav-tfasign').classList.toggle('disabled', !enable);
		document.getElementById('nav-accessibility').classList.toggle('disabled', !enable);
	}

	// 画面遷移関数
	 function navigateTo(page, addHistory = true) {
	
		if (!document.getElementById(page)) {
			console.error(`Page not found: ${page}`);
			return;
		}
	
		document.querySelectorAll('.page').forEach(p => p.classList.add('d-none'));
	
		document.getElementById(page).classList.remove('d-none');
	
		// 🔹 ここでトーナメントリストをロード
		if (page === 'tournament-list') {
			loadTournamentList();
		}
	
		if (addHistory) {
			history.pushState({ page }, '', `#${page}`);
		}
	}

	// 画面切り替え関数
	 function showLogin(addHistory = true) {
		navigateTo('login', addHistory);
	}

	 function showMatchResult(addHistory = true) {
		navigateTo('match-result', addHistory);
	}

	document.addEventListener("DOMContentLoaded", () => {
		const fontSizeSelect = document.getElementById("font-size");
		const contrastSelect = document.getElementById("contrast-mode");
	
		if (fontSizeSelect && contrastSelect) {
			fontSizeSelect.addEventListener("change", () => {
				localStorage.setItem("font-size", fontSizeSelect.value);
				applyAccessibilitySettings();
			});
	
			contrastSelect.addEventListener("change", () => {
				localStorage.setItem("contrast-mode", contrastSelect.value);
				applyAccessibilitySettings();
			});
		}
	});
	
	// ページ読み込み時の処理（URLの `#` を元に復元）
	document.addEventListener('DOMContentLoaded', () => {
		const canvas = document.getElementById("pongCanvas");
		const ctx = canvas ? canvas.getContext("2d") : null;
	
		if (!canvas || !ctx) {
			console.error("Canvasが取得できませんでした");
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
	
		// アクセシビリティ設定を適用
		applyAccessibilitySettings();
	
		// ページ読み込み時にゲーム設定をロード
		if (document.getElementById('game-settings')) {
			loadGameSettings();
		}
	
		// Removed: localStorage.getItem('access_token');
		// enableNavigation(!!token);
	
		// 初回ロード時にURLの `#` に応じて画面を表示
		const page = location.hash.replace('#', '') || 'loginSelection';
		const username2 = localStorage.getItem('username');
		navigateTo(username2 ? page : 'loginSelection', false);
	});

	function applyAccessibilitySettings() {
		const savedFontSize = localStorage.getItem("font-size") || "medium";
		const savedContrast = localStorage.getItem("contrast-mode") || "normal";
	
		// すべてのサイズクラスを削除して、新しい設定を適用
		document.body.classList.remove("font-small", "font-medium", "font-large", "font-xlarge");
		document.body.classList.add(`font-${savedFontSize}`);
	
		// すべてのコントラストクラスを削除して、新しい設定を適用
		document.body.classList.remove("normal", "high-contrast", "dark-mode");
		document.body.classList.add(savedContrast);
	}