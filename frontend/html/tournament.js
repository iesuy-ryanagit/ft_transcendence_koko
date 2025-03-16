
function validateInput2(input) {
    const regex = /^[a-zA-Z0-9]+$/;
    return regex.test(input);
}

async function fetchTournaments() {
	const token = localStorage.getItem('access_token');

	const response = await fetch(TournamentBase + 'tournament/list/', {
		method: 'GET',
		headers: { 'Authorization': 'Bearer ' + token },
        credentials: 'include'  // これでCookieが含まれる
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
	const max_participants = 4;
	const token = localStorage.getItem('access_token');
    if (!validateInput(name)) {
        alert('入力は全て数字かアルファベットでならなければいけない');
        return; // 入力が不正なら処理を中断
    }
	const response = await fetch(TournamentBase + 'tournament/create/', {
		method: 'POST',
		headers: { 
			'Content-Type': 'application/json',
			'Authorization': 'Bearer ' + token
		},
        credentials: 'include',  // これでCookieが含まれる
		body: JSON.stringify({name, max_participants})

	});

	const data = await response.json();

	if (response.ok) {
		navigateTo('dashboard');
	} else {
		alert('作成失敗: ' + (data.message || 'サーバーエラー'));
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
						<button class="btn btn-success" onclick="registerPlayer('${tournament.id}')">プレイヤー登録</button>
						<button class="btn btn-warning" onclick="startTournament('${tournament.id}')"
							${tournament.status === 'ongoing' ? 'disabled' : ''}>
							試合開始
						</button>
					</div>
				</div>
			`).join("");
		})
		.catch(error => {
			console.error("トーナメント一覧の取得に失敗:", error);
			container.innerHTML = "<p>データを取得できませんでした。</p>";
		});
}