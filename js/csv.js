// ============================================================
//  csv.js - CSV出力ユーティリティ（クライアント側）
// ============================================================

/**
 * 1セルの値をCSV安全にエスケープする
 * - 値に , " 改行 CR が含まれる場合は " で囲み、内部の " は "" に変換する
 * - null/undefined は空文字扱い
 */
function csvEscapeCell(value) {
  if (value === null || value === undefined) return '';
  let s = String(value);
  if (/[",\r\n]/.test(s)) {
    s = '"' + s.replace(/"/g, '""') + '"';
  }
  return s;
}

/**
 * 行（配列）→ CSV文字列1行
 */
function csvRow(cells) {
  return cells.map(csvEscapeCell).join(',');
}

/**
 * ヘッダ＋2次元配列をCSV文字列化する
 * - 行区切りは \r\n（Excel互換）
 * - 先頭は呼び出し側で \uFEFF（BOM）を付加する（ダウンロード関数側で付けるため、本関数では付けない）
 */
function buildCsv(headers, rows) {
  const lines = [];
  lines.push(csvRow(headers));
  for (const r of rows) lines.push(csvRow(r));
  return lines.join('\r\n');
}

/**
 * CSVをダウンロードさせる
 * - UTF-8 BOM (\uFEFF) を先頭に付加（Excel 文字化け対策）
 * - Blob + URL.createObjectURL + <a download> 方式
 */
function downloadCsv(filename, headers, rows) {
  const csv  = buildCsv(headers, rows);
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** 今日の日付（YYYY-MM-DD、ローカルタイム） */
function csvTodayStr() {
  const d  = new Date();
  const y  = d.getFullYear();
  const m  = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${dd}`;
}

/** 今月の YYYY-MM */
function csvCurrentMonthStr() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

/** 任意の日付入力を YYYY/MM/DD に整形。失敗時は元の文字列を返す */
function csvFormatDate(v) {
  if (!v) return '';
  try {
    const d = new Date(v);
    if (isNaN(d.getTime())) return String(v);
    const y  = d.getFullYear();
    const m  = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${y}/${m}/${dd}`;
  } catch (e) {
    return String(v);
  }
}
