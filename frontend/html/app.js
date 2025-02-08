export async function fetchHtml(url) {
  console.log("Function fetchHtml started");  // 関数の開始を表示
  const defaultOptions = {
    method: "GET",
    headers: {
      "Content-Type": "application/json", // デフォルトのヘッダー
    },
  };

  try {
    // fetchを実行
    const response = await fetch(url, defaultOptions);

    // エラーハンドリング
    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error:", errorData);
      throw new Error(`HTTP Error: ${response.status}`);
    }

    console.log("API Success:", response);
    return response.text();
  } catch (error) {
    console.error("Fetch Error:", error);
    return `<h1 data-i18n="common:page_not_found">Page not found.</h1>`;
  }
}

window.onload = async function() {
  console.log("Function window.onload started");  // 関数の開始を表示
  const appDiv = document.getElementById("app");

  try {
    const htmlContent = await fetchHtml("http://account:8001/myapp/");
    appDiv.innerHTML = htmlContent;
  } catch (error) {
    appDiv.innerHTML = `<h1>Error: ${error.message}</h1>`;
  }
};

