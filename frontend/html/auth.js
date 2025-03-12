

// ログイン処理
 async function login_action() {
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

// ユーザープロフィール取得
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

 { showTFARegister,login, fetchUserProfile, loginWith2FA, logout , Goto42Oauth, loginWith42Oauth, signUp, setUpTfa};
