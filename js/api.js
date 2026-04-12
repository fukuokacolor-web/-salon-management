// ============================================================
//  api.js - GAS API呼び出し
// ============================================================

/**
 * GAS APIを呼び出す共通関数
 */
async function apiGet(action, params = {}) {
  try {
    const query = new URLSearchParams({
      action,
      key: getApiKey(),
      ...params,
    });
    const res  = await fetch(`${GAS_URL}?${query}`, { redirect: 'follow' });
    const data = await res.json();
    if (data.error === 'unauthorized') {
      logout();
      return null;
    }
    return data;
  } catch (err) {
    console.error(`API error [${action}]:`, err);
    return null;
  }
}

/** ダッシュボードデータ取得 */
async function getDashboard() {
  return apiGet('getDashboard');
}

/** 予約一覧取得（month: "yyyy/MM"） */
async function getReservations(month) {
  return apiGet('getReservations', month ? { month } : {});
}

/** 顧客一覧取得 */
async function getCustomers() {
  return apiGet('getCustomers');
}

/** 予約をキャンセル */
async function cancelReservation(row) {
  return apiGet('cancelReservation', { row });
}
