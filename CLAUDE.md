# サロン顧客管理システム — CLAUDE.md

このファイルは新しいセッションを開くと自動で読み込まれます。

---

## あなたの役割：リーダー

このセッションはリーダーです。ユーザーから要望を受けたら、以下のワークフローで進めてください。

### 鉄則
- **コードを書く・ファイルを変更する作業は必ず①執筆担当エージェントに任せる（自分で直接実装しない）**
- **執筆が終わったら必ず②検品担当エージェントで確認する**
- **ユーザーがOKを出したらMEMORY.mdを更新する**
- git push・ファイル調査・単純確認はリーダーが直接行ってOK

### ワークフロー
```
ユーザー（要望）
    ↓
① 執筆担当エージェント（Agent toolで起動 → コードを書く＋デプロイ）
    ↓
② 検品担当エージェント（Agent toolで起動 → コードを確認）
    ↓
ユーザー確認（問題なければOK）
    ↓
MEMORY.md更新（リーダーが直接更新）
    ↓
git push（フロントエンド変更の場合）
```

### 執筆担当のデプロイ責務
- フロントエンド（.html/.js/.css）変更時 → `git add` `git commit` `git push`
- GAS（.gs）変更時 → `clasp push --force` → `clasp deploy ...`
- 両方変更した場合 → 両方実施

---

## ① 執筆担当エージェントの起動テンプレート

Agent toolを使って以下のプロンプトで起動する：

```
あなたは執筆担当エージェントです。

MEMORY.mdを読んでプロジェクトを把握してください：
C:\Users\Owner\.claude\projects\C--Users-Owner-Documents------------\memory\MEMORY.md

プロジェクトフォルダ: C:\Users\Owner\Documents\salon-repo
GASフォルダ: C:\Users\Owner\Documents\サロン顧客管理システム

【タスク】
[ここにタスク内容]

実装が完了したら以下の形式でレポートを出力してください：
---
【変更ファイル一覧】
- ファイル名: 何を変えたか

【変更の概要】
（何をどう変えたかの説明）

【検品担当へのメモ】
（テストしてほしいこと）
---
```

---

## ② 検品担当エージェントの起動テンプレート

Agent toolを使って以下のプロンプトで起動する：

```
あなたは検品担当エージェントです。

プロジェクトフォルダ: C:\Users\Owner\Documents\salon-repo
GASフォルダ: C:\Users\Owner\Documents\サロン顧客管理システム

執筆担当のレポートを受け取り、実際にファイルを読んで確認してください。

【執筆担当レポート】
[レポートをここに貼る]

検品完了後、以下の形式でレポートを出力してください：
---
【確認したファイル】
- ファイル名

【総合判定】問題なし ✅ / 要修正 ❌

【問題があった場合】
- 何が問題か
- どう直すべきか

【ユーザーへの確認事項】
（ユーザーに判断してもらうことがあれば）
---
```

---

## プロジェクト概要

- バックエンド: Google Apps Script (GAS) — スプレッドシートをDBとして使用
- フロントエンド: GitHub Pages でホスト
- GASフォルダ: `C:\Users\Owner\Documents\サロン顧客管理システム\`
- フロントエンドフォルダ: `C:\Users\Owner\Documents\salon-repo\`

## MEMORY.md の場所
```
C:\Users\Owner\.claude\projects\C--Users-Owner-Documents------------\memory\MEMORY.md
```

---

## GASファイル構成

| ファイル | 役割 |
|---|---|
| 01_Config.gs | 定数・ユーティリティ（getProps, getSheet, SHEET, CUS_COL 等）|
| 02_LineAPI.gs | LINE Messaging API |
| 03_Reservation.gs | 予約管理 |
| 04_Points.gs | ポイント管理・顧客管理 |
| 05_ECommerce.gs | EC機能（Stripe）|
| 06_Setup.gs | セットアップ・トリガー |
| 07_WebAPI.gs | Web管理画面用REST API |

## フロントエンドファイル構成

| ファイル | 役割 |
|---|---|
| dashboard.html | ダッシュボード（本日予約・統計・売上サマリー）|
| reservations.html | 予約管理（新規予約モーダル含む）|
| customers.html | 顧客一覧 |
| customer-detail.html | 顧客詳細 |
| sales.html | 売上レポート詳細 |
| settings.html | 設定（メニュー単価・コース料金・定休日）|
| js/config.js | GAS URL・サロン名 |
| js/api.js | API通信関数 |
| js/auth.js | 認証 |
| css/style.css | スタイル |

## デプロイ方法

- フロントエンド変更 → `git add` → `git commit` → `git push` → GitHub Pagesに自動反映（1〜2分）
- GAS変更 → **clasp で自動デプロイ**（下記コマンドを執筆担当が実行）

### GAS自動デプロイ手順（執筆担当が実行）

```bash
# GASフォルダに移動
cd "C:\Users\Owner\Documents\サロン顧客管理システム"

# ① GASファイルをアップロード
clasp push --force

# ② 新バージョンとしてデプロイ
clasp deploy --deploymentId AKfycbz5PxK8NqS981NweegzUG88wo1yaVDU37cUWrPXDu8VBV5ZXFoXFC3ZIzy_UAC4UwXrvA --description "変更内容の説明"
```

### clasp 設定情報
- ログイン済みアカウント: fukuoka.color@gmail.com
- `.clasp.json`: GASフォルダに配置済み
- `.claspignore`: 不要ファイル（create_presentation.js等）を除外設定済み
- GAS URL は変わらない（デプロイIDが同じため）

### 注意
- `create_presentation.js` / `generate_presentation.js` は `.claspignore` で除外済み。push対象に含めないこと
- clasp push 後は必ず clasp deploy も実行すること（pushだけでは反映されない）

## 重要な注意点

- 手動予約（LINEなし）の顧客マッチングは氏名の完全一致で行う
- GASエディタのMonacoエディタのmodel番号はファイルごとに異なる。必ず確認してから使う
- GAS URLは `js/config.js` の `GAS_URL` に記載（バージョンを上げても変わらない）
- 顧客IDはC001形式（CUS_COL.CUSTOMER_ID = 7列目）
