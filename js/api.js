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

/** プラン設定（都度払い / 回数コース） */
async function setPlan(customerId, plan, courseTotal, courseName) {
  return apiGet('setPlan', { customerId, plan, courseTotal: String(courseTotal || ''), courseName: courseName || '' });
}

/** メニュー単価設定取得 */
async function getMenuPrices() {
  return apiGet('getMenuPrices');
}

/** メニュー単価設定保存 */
async function saveMenuPrices(menuPrices) {
  return apiGet('saveMenuPrices', { menuPrices: JSON.stringify(menuPrices) });
}

/** 売上レポート取得（months: 集計月数） */
async function getSalesReport(months = 6) {
  return apiGet('getSalesReport', { months: String(months) });
}

/** 定休日設定取得 */
async function getClosedDays() {
  return apiGet('getClosedDays');
}

/** 定休日設定保存 */
async function saveClosedDays(dates, weekdays) {
  return apiGet('saveClosedDays', {
    dates:    JSON.stringify(dates),
    weekdays: JSON.stringify(weekdays),
  });
}

/** 予約を新規保存（顧客自動作成つき） */
async function saveReservation(params) {
  return apiGet('saveReservation', params);
}

/** コース料金設定取得 */
async function getCoursePrices() {
  return apiGet('getCoursePrices');
}

/** コース料金設定保存 */
async function saveCoursePrices(coursePrices) {
  return apiGet('saveCoursePrices', { coursePrices: JSON.stringify(coursePrices) });
}

/** 支払いを記録 */
async function recordPayment(params) {
  return apiGet('recordPayment', params);
}

/** 支払い履歴取得 */
async function getPaymentHistory(customerId) {
  return apiGet('getPaymentHistory', { customerId });
}

// ─── ポイント交換システム API ──────────────────────────────────

/** 電話番号で顧客を検索（認証不要） */
async function checkPhone(phone) {
  return apiGet('checkPhone', { phone });
}

/** パスワード登録（認証不要） */
async function registerPassword(customerId, hashedPassword) {
  return apiGet('registerPassword', { customerId, hashedPassword });
}

/** 電話番号＋ハッシュパスワードでログイン（認証不要） */
async function loginWithPassword(phone, hashedPassword) {
  return apiGet('loginWithPassword', { phone, hashedPassword });
}

/** 交換対象商品一覧取得（認証不要） */
async function getExchangeProducts() {
  return apiGet('getExchangeProducts');
}

/** 交換申請（認証不要） */
async function applyExchange(customerId, productId) {
  return apiGet('applyExchange', { customerId, productId });
}

/** 交換申請一覧取得（管理者APIキー必要） */
async function getExchangeRequests(status) {
  return apiGet('getExchangeRequests', { status: status || '' });
}

/** 交換申請を完了にする（管理者APIキー必要） */
async function approveExchange(requestId) {
  return apiGet('approveExchange', { requestId });
}

/** 交換申請を却下する（管理者APIキー必要） */
async function rejectExchange(requestId) {
  return apiGet('rejectExchange', { requestId });
}

/** 交換商品の追加・更新（管理者APIキー必要） */
async function saveExchangeProduct(params) {
  return apiGet('saveExchangeProduct', params);
}

/** 交換商品を削除（管理者APIキー必要） */
async function deleteExchangeProduct(productId) {
  return apiGet('deleteExchangeProduct', { productId });
}

/** 予約を編集（日時・メニュー変更） */
async function updateReservation(row, date, menu) {
  return apiGet('updateReservation', { row, date, menu });
}

/** コース種別一覧・料金取得 */
async function getCourseTypes() {
  return apiGet('getCourseTypes');
}

/** コース種別・料金保存 */
async function saveCourseTypes(types, coursePrices) {
  return apiGet('saveCourseTypes', {
    types: JSON.stringify(types),
    coursePrices: JSON.stringify(coursePrices),
  });
}

/** コース残回数を相対値で調整（+1/-1等） */
async function adjustCourseRemaining(customerId, delta) {
  return apiGet('adjustCourseRemaining', { customerId, delta: String(delta) });
}

/** コース残回数を絶対値でセット */
async function setCourseRemaining(customerId, value) {
  return apiGet('setCourseRemaining', { customerId, value: String(value) });
}

/** 顧客パスワードリセット（管理者） */
async function resetCustomerPassword(customerId) {
  return apiGet('resetCustomerPassword', { customerId });
}

/** キャンセルポリシー文言を取得 */
async function getCancelPolicy() {
  return apiGet('getCancelPolicy');
}

/** キャンセルポリシー文言を保存 */
async function saveCancelPolicy(text) {
  return apiGet('saveCancelPolicy', { text: text || '' });
}

/** バックアップ警告閾値（日数）を取得 */
async function getBackupStaleDays() {
  return apiGet('getBackupStaleDays');
}

/** バックアップ警告閾値（日数）を保存 */
async function saveBackupStaleDays(days) {
  return apiGet('saveBackupStaleDays', { days: String(days) });
}
