const apiBase = 'http://localhost:8000/api/';

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch(apiBase + 'login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('username', username);  // ユーザー名を保存
		enableNavigation(true);  // 🔥 ログイン後にメニューを有効化
        navigateTo('dashboard');  // 修正: showDashboard() → navigateTo()
    } else {
        alert('ログイン失敗: ' + (data.message || 'サーバーエラー'));
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
    }

    // ブラウザ履歴を追加
    if (addHistory) {
        history.pushState({ page }, '', `#${page}`);
    }
}

async function fetchTournaments() {
    const token = localStorage.getItem('access_token');
    console.log('トークン:', token);  // トークンが取得できているか確認

    const response = await fetch(apiBase + 'tournaments/', {
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + token }
    });

    const data = await response.json();
    console.log('トーナメント取得レスポンス:', data);  // レスポンス確認

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

    console.log('トーナメント作成:', name); // デバッグ用

    const response = await fetch(apiBase + 'tournaments/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ name })
    });

    const data = await response.json();
    console.log('トーナメント作成レスポンス:', data);  // レスポンス確認

    if (response.ok) {
        navigateTo('dashboard');
    } else {
        alert('作成失敗: ' + (data.message || 'サーバーエラー'));
    }
}


// 画面切り替え関数
function showLogin(addHistory = true) {
    navigateTo('login', addHistory);
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

// ログアウト処理
function logout() {
    localStorage.removeItem('access_token');
    enableNavigation(false);
    showLogin(true);
}


// ページ読み込み時の処理（URLの `#` を元に復元）
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    enableNavigation(!!token);
    const page = location.hash.replace('#', '') || 'login';
    navigateTo(token ? page : 'login', false);
});


// 初回ロード時にURLの `#` に応じて画面を表示
document.addEventListener('DOMContentLoaded', () => {
    const page = location.hash.replace('#', '') || 'login';
    navigateTo(page, false);
});
