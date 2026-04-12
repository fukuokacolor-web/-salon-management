// ============================================================
//  auth.js - 認証管理
// ============================================================

const AUTH_KEY = 'salon_api_key';

/**
 * ログイン処理
 */
async function login(password) {
  try {
    const url = GAS_URL + '?action=login&password=' + encodeURIComponent(password);
    const res  = await fetch(url, { redirect: 'follow' });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch(e) {
      console.error('JSON parse error:', text);
      return { success: false, message: 'サーバーからの応答が不正です。' };
    }
    if (data.success && data.key) {
      localStorage.setItem(AUTH_KEY, data.key);
      return { success: true };
    }
    return { success: false, message: data.message || 'パスワードが違います' };
  } catch (err) {
    console.error('login error:', err);
    return { success: false, message: 'サーバーに接続できません。GAS URLを確認してください。' };
  }
}

/**
 * ログアウト
 */
function logout() {
  localStorage.removeItem(AUTH_KEY);
  window.location.href = 'index.html';
}

/**
 * 認証チェック（各ページの先頭で呼ぶ）
 */
function checkAuth() {
  if (!localStorage.getItem(AUTH_KEY)) {
    window.location.href = 'index.html';
    return false;
  }
  return true;
}

/**
 * 保存済みAPIキーを取得
 */
function getApiKey() {
  return localStorage.getItem(AUTH_KEY) || '';
}
