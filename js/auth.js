// ============================================================
//  auth.js - 認証管理
// ============================================================

const AUTH_KEY = 'salon_api_key';

/**
 * ログイン処理
 * GASにパスワードを送ってAPIキーを取得・保存する
 */
async function login(password) {
  try {
    const url = `${GAS_URL}?action=login&password=${encodeURIComponent(password)}`;
    const res  = await fetch(url, { redirect: 'follow' });
    const data = await res.json();
    if (data.success && data.key) {
      sessionStorage.setItem(AUTH_KEY, data.key);
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
  sessionStorage.removeItem(AUTH_KEY);
  window.location.href = 'index.html';
}

/**
 * 認証チェック（各ページの先頭で呼ぶ）
 */
function checkAuth() {
  if (!sessionStorage.getItem(AUTH_KEY)) {
    window.location.href = 'index.html';
    return false;
  }
  return true;
}

/**
 * 保存済みAPIキーを取得
 */
function getApiKey() {
  return sessionStorage.getItem(AUTH_KEY) || '';
}
