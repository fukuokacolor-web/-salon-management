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
    const res  = await fetch(`${GAS_URL}?${query}`, {
      redirect: 'follow',
      mode: 'cors',
    });

    // レスポンスのテキストを取得してからJSONをパース
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      console.error('JSON parse error:', text);
      return null;
    }

    if (data.error === 'unauthorized') {
      // unauthorizedの場合はログアウトせず、再ログインを促す
      console.warn('API unauthorized - セッション切れの可能性があります');
      sessionStorage.removeItem('salon_api_key');
      window.location.href = 'index.html';
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

/** 予約を完了（来店記録＋ポイント付与） */
async function completeReservation(row) {
  return apiGet('completeReservation', { row });
}

/** 顧客詳細・来店記録取得 */
async function getCustomerDetail(customerId) {
  return apiGet('getCustomerDetail', { customerId });
}

/** メニュー別ポイント設定取得 */
async function getMenuPoints() {
  return apiGet('getMenuPoints');
}

/** メニュー別ポイント設定保存 */
async function saveMenuPoints(menuPoints) {
  return apiGet('saveMenuPoints', { menuPoints: JSON.stringify(menuPoints) });
}
