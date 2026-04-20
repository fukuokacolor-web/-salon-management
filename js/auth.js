// ============================================================
//  auth.js - 認証管理
// ============================================================

const AUTH_KEY     = 'salon_api_key';
const REMEMBER_KEY = 'salon_remember';

/**
 * ログイン保持状態に応じたストレージを返す
 */
function getStore() {
  return localStorage.getItem(REMEMBER_KEY) === '1' ? localStorage : sessionStorage;
}

/**
 * ログイン処理
 * @param {string} password
 * @param {boolean} remember ログイン状態を保持するか
 */
async function login(password, remember) {
  try {
    // CORS preflight を回避するため Content-Type は text/plain で送信
    // （GAS側で JSON.parse する）
    const res = await fetch(GAS_URL, {
      method: 'POST',
      redirect: 'follow',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({ action: 'adminLogin', password: password }),
    });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch(e) {
      console.error('JSON parse error:', text);
      return { success: false, message: 'サーバーからの応答が不正です。' };
    }
    if (data.success && data.key) {
      // 一旦両方クリアしてから保存先を切り替え
      localStorage.removeItem(AUTH_KEY);
      sessionStorage.removeItem(AUTH_KEY);
      if (remember) {
        localStorage.setItem(REMEMBER_KEY, '1');
        localStorage.setItem(AUTH_KEY, data.key);
      } else {
        localStorage.removeItem(REMEMBER_KEY);
        sessionStorage.setItem(AUTH_KEY, data.key);
      }
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
  sessionStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(REMEMBER_KEY);
  window.location.href = 'index.html';
}

/**
 * 認証チェック（各ページの先頭で呼ぶ）
 */
function checkAuth() {
  const key = localStorage.getItem(AUTH_KEY) || sessionStorage.getItem(AUTH_KEY);
  if (!key) {
    window.location.href = 'index.html';
    return false;
  }
  return true;
}

/**
 * 保存済みAPIキーを取得
 */
function getApiKey() {
  return localStorage.getItem(AUTH_KEY) || sessionStorage.getItem(AUTH_KEY) || '';
}
