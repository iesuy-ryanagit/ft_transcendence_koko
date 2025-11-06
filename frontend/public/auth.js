function validateInput(input) {
    const regex = /^[a-zA-Z0-9]+$/;
    return regex.test(input);
}

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    for (let c of cookies) {
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.split('=')[1]);
        }
    }
    return null;
}

// In-memory token manager: stores JWT only in memory (cleared on reload)
// NOTE: token handling is now delegated to httpOnly cookies set by the server.
// Client will not store or read JWTs in JS to reduce XSS risk.



// ログイン処理
 async function login_action() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    if (!validateInput(username)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
    if (!validateInput(password)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
    const response = await fetch(apiBase + 'login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
	if (response.ok) {
		// Server sets httpOnly cookie for auth; do not store token in JS
		localStorage.setItem('username', username);
		await fetchUserProfile();
        enableNavigation(true);
        navigateTo('dashboard');
    } else {
        alert('ログイン失敗: ' + (data.message || 'サーバーエラー'));
    }
}

// ユーザープロフィール取得
async function fetchUserProfile() {
	try {
		// Server-authenticated via httpOnly cookie; include credentials so cookie is sent
		const response = await fetch(apiBase + 'profile/', {
			method: 'GET',
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

    } catch (error) {
        console.error('プロフィール取得エラー:', error);
    }
}

async function loginWith2FA() {
	const username = document.getElementById('tfalogin-username').value;
	const password = document.getElementById('tfalogin-password').value;
	const otp = document.getElementById('tfalogin-token').value;
    if (!validateInput(username)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
    if (!validateInput(password)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
    if (!validateInput(otp)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }

    
	const response = await fetch(apiBase + 'login-tfa/', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json'},
		credentials: 'include',
		body: JSON.stringify({ username, password, otp })
	});

	const data = await response.json();
	if (response.ok) {
		// Server sets httpOnly cookie for auth; do not store token in JS
		localStorage.setItem('username', username);
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

		// Server sets httpOnly cookie for auth; client does not store JWT in JS

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
    if (!validateInput(username)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
    if (!validateInput(password)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
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
    const csrfToken = getCookie('csrftoken');
	const response = await fetch(apiBase + 'setup-tfa/', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json', 
        'X-CSRFToken': csrfToken
        },
		credentials: 'include'  // 必要なら追加
	});

	const data = await response.json();
	if (response.ok) {
		alert('セットアップ成功!');
	} else {
		alert('セットアップ失敗: ' + data.message);
	}
}

// ログアウト処理
async function logout() {
	const response = await fetch(apiBase + 'logout/', {
		method: 'GET',
		headers: { 'Content-Type': 'application/json' },
		credentials: 'include'  // 必要なら追加
	});

	const data = await response.json();
	if (response.ok) {
		alert('ログアウト成功!');
	} else {
		alert('ログアウト失敗');
	}
	// 他のユーザー情報はlocalStorageに残っている可能性があるため個別に削除する
	localStorage.removeItem('username');
	localStorage.removeItem('email');
	localStorage.removeItem('opt');

    // ナビゲーション無効化
    enableNavigation(false);

    // `history.pushState()` をクリアして `popstate` が発火しないようにする
    history.pushState(null, '', location.pathname);  // これで `hash` をリセット

    // `history.replaceState()` を使用して履歴を書き換え
    history.replaceState({}, '', '#loginSelection');

    // 画面を遷移
    navigateTo('loginSelection', false);
}

async function fetchTFAQRCode() {
	try {
		// Server-authenticated via httpOnly cookie; include credentials so cookie is sent
		const response = await fetch(apiBase + 'setup-tfa/', {
			method: "GET",
			headers: {
				"Content-Type": "application/json"
			},
			credentials: 'include',
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.message || "2FAのQRコード取得に失敗しました");
		}

		const data = await response.json();
		displayQRCode(data.qr_url, data.secret_key);

	} catch (error) {
		alert(`エラー: ${error.message}`);
	}
}

async function sendTFAExitRequest() {
	try {
		const response = await fetch(apiBase + 'setup-tfa/',  {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			credentials: 'include',
			body: JSON.stringify({ action: "exit_2fa" }) 
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.message || "APIリクエストに失敗しました");
		}

	} catch (error) {
		console.error("エラー:", error);
	}
}

async function showTFARegister(addHistory = true) {
	await fetchTFAQRCode(); // QRコード取得を待つ
	navigateTo('TFAregister', addHistory);

	// 2FA登録画面が表示されたらボタンを取得
	const observer = new MutationObserver((mutations, obs) => {
		const backButton = document.querySelector("#TFAregister .btn-secondary");
		if (backButton && !document.getElementById('TFAregister').classList.contains('d-none')) {
			backButton.addEventListener("click", async function () {
				await sendTFAExitRequest();
				navigateTo("dashboard");
			});
			obs.disconnect(); // イベント登録後に監視を停止
		}
	});

	observer.observe(document.getElementById('TFAregister'), { attributes: true, attributeFilter: ['class'] });
}


function displayQRCode(otpAuthUrl, secretKey) {
	
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

 { showTFARegister,login, fetchUserProfile, loginWith2FA, logout , Goto42Oauth, loginWith42Oauth, signUp, setUpTfa};
