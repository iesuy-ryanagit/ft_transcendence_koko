const apiBase = 'http://localhost:8000/api/';

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
    const username = document.getElementById('login2fa-username').value;
    const password = document.getElementById('login2fa-password').value;
    const token = document.getElementById('login2fa-token').value;

    const response = await fetch(apiBase + 'login-2fa/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password, token })
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
        alert('2FAログイン失敗: ' + (data.message || 'サーバーエラー'));
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

function enableNavigation(enable) {
    document.getElementById('nav-dashboard').classList.toggle('disabled', !enable);
    document.getElementById('nav-profile').classList.toggle('disabled', !enable);
    document.getElementById('nav-logout').classList.toggle('disabled', !enable);
	document.getElementById('nav-tfasign').classList.toggle('disabled', !enable);
}

// 画面遷移関数
function navigateTo(page, addHistory = true) {
    // すべての画面を非表示にする
    document.querySelectorAll('.page').forEach(page => page.classList.add('d-none'));

    // 表示するページを決定
    if (page === 'login') {
        document.getElementById('login').classList.remove('d-none');
    } else if (page === 'signup') {
        document.getElementById('signup').classList.remove('d-none');
    } else if (page === 'dashboard') {
        document.getElementById('dashboard').classList.remove('d-none');
        fetchTournaments();
    } else if (page === 'create-tournament') {
        document.getElementById('create-tournament').classList.remove('d-none');
    } else if (page === 'match-result') {
        document.getElementById('match-result').classList.remove('d-none');
    } else if (page == 'TFAregister'){
		document.getElementById('TFAregister').classList.remove('d-none');
	} else if (page = 'loginSelection'){
		document.getElementById('loginSelection').classList.remove('d-none');
	} else if (page === 'login-2fa') {
        document.getElementById('login-2fa').classList.remove('d-none');
	}

    // ブラウザ履歴を追加
    if (addHistory) {
        history.pushState({ page }, '', `#${page}`);
    }
}

async function fetchTournaments() {
    const token = localStorage.getItem('access_token');

    const response = await fetch(apiBase + 'tournaments/', {
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
    const token = localStorage.getItem('access_token');

    const response = await fetch(apiBase + 'tournaments/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ name })
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
        const response = await fetch(apiBase + 'signup-tfa/', {
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
	navigateTo('loginSelect', addHistory);
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
    localStorage.removeItem('access_token');
    enableNavigation(false);
    showLoginSelect(true);
}


// ページ読み込み時の処理（URLの `#` を元に復元）
document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.querySelector("#TFAregister .btn-secondary");

    if (backButton) {
        backButton.addEventListener("click", async function () {
            await sendTFAExitRequest();
            navigateTo("dashboard");
        });
    }

    const token = localStorage.getItem('access_token');
    enableNavigation(!!token);

    // 初回ロード時にURLの `#` に応じて画面を表示
    const page = location.hash.replace('#', '') || 'loginSelection';
    navigateTo(token ? page : 'loginSelection', false);
});
