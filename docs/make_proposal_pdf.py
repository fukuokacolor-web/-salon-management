# -*- coding: utf-8 -*-
"""
サロン顧客管理システム 提案資料 (.pdf) 生成スクリプト
出力: SALON_PROPOSAL.pdf (16:9 相当 338x190mm, 20ページ)
reportlab canvas 直接描画版（PowerPoint不要）
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ========== フォント登録 ==========
pdfmetrics.registerFont(TTFont('Meiryo', 'C:/Windows/Fonts/meiryo.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('MeiryoBold', 'C:/Windows/Fonts/meiryob.ttc', subfontIndex=0))
FONT = 'Meiryo'
FONT_B = 'MeiryoBold'

# ========== ページサイズ（16:9 相当） ==========
PAGE_W = 338 * mm
PAGE_H = 190 * mm

# ========== カラー ==========
ROSE       = HexColor('#D4688A')
DARK_ROSE  = HexColor('#7B4A5C')
GOLD       = HexColor('#D4A574')
BG_PINK    = HexColor('#FFF5F7')
LIGHT_PINK = HexColor('#FFE4EC')
WHITE      = HexColor('#FFFFFF')
BLACK      = HexColor('#333333')
GRAY       = HexColor('#888888')
LIGHT_GRAY = HexColor('#EEEEEE')
DARK       = HexColor('#222222')
GREEN      = HexColor('#4CAF50')
ORANGE     = HexColor('#E89B3C')
RED        = HexColor('#E53935')
LINE_GREEN = HexColor('#06C755')

TOTAL = 20

# ========== ヘルパー ==========
def fill_rect(c, x, y, w, h, color, stroke=False, stroke_color=None, stroke_w=0.5):
    c.setFillColor(color)
    if stroke and stroke_color is not None:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_w)
        c.rect(x, y, w, h, stroke=1, fill=1)
    else:
        c.rect(x, y, w, h, stroke=0, fill=1)

def stroke_rect(c, x, y, w, h, color, lw=1.0):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.rect(x, y, w, h, stroke=1, fill=0)

def rounded(c, x, y, w, h, r, fill_color=None, stroke_color=None, lw=1.0):
    do_fill = 1 if fill_color is not None else 0
    do_stroke = 1 if stroke_color is not None else 0
    if fill_color is not None:
        c.setFillColor(fill_color)
    if stroke_color is not None:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, stroke=do_stroke, fill=do_fill)

def circle(c, cx, cy, r, fill_color=None, stroke_color=None, lw=1.0):
    do_fill = 1 if fill_color is not None else 0
    do_stroke = 1 if stroke_color is not None else 0
    if fill_color is not None:
        c.setFillColor(fill_color)
    if stroke_color is not None:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(lw)
    c.circle(cx, cy, r, stroke=do_stroke, fill=do_fill)

def draw_text(c, x, y, text, *, font=FONT, size=11, color=BLACK, align='left'):
    """y はベースライン。"""
    c.setFont(font, size)
    c.setFillColor(color)
    if align == 'left':
        c.drawString(x, y, text)
    elif align == 'center':
        c.drawCentredString(x, y, text)
    elif align == 'right':
        c.drawRightString(x, y, text)

def draw_multiline(c, x, y_top, text, *, font=FONT, size=11, color=BLACK,
                   align='left', line_height=None, box_w=None):
    """y_top はテキストブロックの上端。行を下方向に描画。"""
    if line_height is None:
        line_height = size * 1.4
    c.setFont(font, size)
    c.setFillColor(color)
    lines = text.split('\n')
    cur_y = y_top - size  # first baseline
    for line in lines:
        if align == 'left':
            c.drawString(x, cur_y, line)
        elif align == 'center':
            cx = x + (box_w / 2 if box_w else 0)
            c.drawCentredString(cx, cur_y, line)
        elif align == 'right':
            cx = x + (box_w if box_w else 0)
            c.drawRightString(cx, cur_y, line)
        cur_y -= line_height

def draw_text_in_box(c, x, y, w, h, text, *, font=FONT, size=11, color=BLACK,
                     align='center', valign='middle', line_height=None):
    """矩形内の中央/左右寄せ・上下寄せでテキスト描画。"""
    if line_height is None:
        line_height = size * 1.4
    lines = text.split('\n')
    total_h = line_height * len(lines)
    if valign == 'middle':
        top = y + h / 2 + total_h / 2
    elif valign == 'top':
        top = y + h
    else:  # bottom
        top = y + total_h
    draw_multiline(c, x, top, text, font=font, size=size, color=color,
                   align=align, line_height=line_height, box_w=w)

# 矢印（右向き三角ブロック）
def right_arrow(c, x, y, w, h, fill_color):
    c.setFillColor(fill_color)
    c.setStrokeColor(fill_color)
    # 本体矩形 + 三角
    body_w = w * 0.6
    p = c.beginPath()
    p.moveTo(x, y + h * 0.3)
    p.lineTo(x + body_w, y + h * 0.3)
    p.lineTo(x + body_w, y)
    p.lineTo(x + w, y + h / 2)
    p.lineTo(x + body_w, y + h)
    p.lineTo(x + body_w, y + h * 0.7)
    p.lineTo(x, y + h * 0.7)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

# ========== 共通装飾 ==========
def add_borders(c):
    """上下の細ライン"""
    # 上：細ピンク
    fill_rect(c, 0, PAGE_H - 5 * mm, PAGE_W, 5 * mm, ROSE)
    # 下：薄いゴールド
    fill_rect(c, 0, 0, PAGE_W, 3 * mm, GOLD)

def add_title_bar(c, title, num):
    """左上に番号丸、タイトル、下線。"""
    add_borders(c)
    # 番号丸
    cx = 18 * mm
    cy = PAGE_H - 18 * mm
    circle(c, cx, cy, 7 * mm, fill_color=ROSE)
    draw_text_in_box(c, cx - 7*mm, cy - 7*mm, 14*mm, 14*mm, f"{num:02d}",
                     font=FONT_B, size=14, color=WHITE, align='center', valign='middle')
    # タイトル
    draw_text(c, 30 * mm, cy - 3 * mm, title,
              font=FONT_B, size=22, color=DARK_ROSE, align='left')
    # タイトル下 金ライン
    fill_rect(c, 12 * mm, PAGE_H - 28 * mm, PAGE_W - 24 * mm, 0.6 * mm, GOLD)

def add_footer(c, num):
    """左下：商品名／右下：N / 20"""
    draw_text(c, 12 * mm, 6 * mm, "サロン顧客管理システム ご提案資料",
              font=FONT, size=8, color=GRAY, align='left')
    draw_text(c, PAGE_W - 12 * mm, 6 * mm, f"- {num} / {TOTAL} -",
              font=FONT, size=8, color=GRAY, align='right')


# ================================================================
# 以下、各スライド描画関数
# ================================================================

def slide01(c):
    """表紙"""
    # 背景
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, BG_PINK)
    # 装飾帯
    fill_rect(c, 0, PAGE_H - 6 * mm, PAGE_W, 6 * mm, ROSE)
    fill_rect(c, 0, 0, PAGE_W, 6 * mm, ROSE)
    # 中央の丸
    circle(c, PAGE_W / 2, PAGE_H - 52 * mm, 18 * mm, fill_color=ROSE)
    # 装飾文字（花記号）
    draw_text_in_box(c, PAGE_W/2 - 20*mm, PAGE_H - 72*mm, 40*mm, 40*mm,
                     "SALON", font=FONT_B, size=28, color=WHITE,
                     align='center', valign='middle')
    # タイトル
    draw_text(c, PAGE_W/2, PAGE_H - 95 * mm, "LINEで予約が完結する",
              font=FONT_B, size=30, color=DARK_ROSE, align='center')
    draw_text(c, PAGE_W/2, PAGE_H - 112 * mm, "サロン顧客管理システム",
              font=FONT_B, size=40, color=ROSE, align='center')
    # サブタイトル
    draw_text(c, PAGE_W/2, PAGE_H - 132 * mm, "オーナー様向け ご提案資料",
              font=FONT, size=18, color=DARK_ROSE, align='center')
    # バージョン
    draw_text(c, PAGE_W/2, PAGE_H - 150 * mm, "Version 1.0  |  2026.XX",
              font=FONT, size=11, color=GRAY, align='center')
    # Thank you 的アクセント
    draw_text(c, PAGE_W/2, 15 * mm, "for Salon Owners",
              font=FONT, size=10, color=DARK_ROSE, align='center')

def slide02(c):
    """こんなお悩みありませんか？"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "こんなお悩みありませんか？", 2)
    draw_text(c, 15 * mm, PAGE_H - 38 * mm,
              "一つでも当てはまれば、このシステムで解決できます。",
              font=FONT, size=14, color=DARK_ROSE)
    worries = [
        "予約の電話・LINEメッセージ対応に追われている",
        "無断キャンセルや常連の予約忘れが多い",
        "顧客ごとのコース残回数の管理が大変",
        "エクセル管理でデータが散らばっている",
        "スマホで業務確認したいが既存システムは重い",
    ]
    # カード高さ、間隔
    top_y = PAGE_H - 50 * mm
    card_h = 18 * mm
    gap = 4 * mm
    for i, w in enumerate(worries):
        y = top_y - (card_h + gap) * i - card_h
        rounded(c, 20 * mm, y, PAGE_W - 40 * mm, card_h, 3*mm,
                fill_color=BG_PINK, stroke_color=ROSE, lw=1.0)
        # チェックボックス
        cb_size = 8 * mm
        cb_x = 26 * mm
        cb_y = y + (card_h - cb_size) / 2
        fill_rect(c, cb_x, cb_y, cb_size, cb_size, WHITE,
                  stroke=True, stroke_color=ROSE, stroke_w=1.2)
        draw_text_in_box(c, cb_x, cb_y, cb_size, cb_size, "[ ]",
                         font=FONT_B, size=9, color=ROSE, align='center', valign='middle')
        # テキスト
        draw_text(c, cb_x + cb_size + 6 * mm, y + card_h/2 - 2, w,
                  font=FONT_B, size=16, color=BLACK, align='left')
    add_footer(c, 2)

def slide03(c):
    """このシステムが解決します"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "このシステムが解決します", 3)
    # メインコピー帯
    rounded(c, 30 * mm, PAGE_H - 60 * mm, PAGE_W - 60 * mm, 22 * mm, 4*mm,
            fill_color=ROSE)
    draw_text_in_box(c, 30*mm, PAGE_H - 60*mm, PAGE_W - 60*mm, 22*mm,
                     "予約・顧客・ポイント・売上。すべてを一つに。",
                     font=FONT_B, size=24, color=WHITE, align='center', valign='middle')
    # 3本柱
    cols = [
        ("LINE予約", "24時間いつでも受付\nアプリ不要"),
        ("管理画面", "スマホ・PC対応\nどこでも確認"),
        ("自動化",  "リマインド・バックアップ\n手間なし"),
    ]
    card_w = 85 * mm
    card_h = 75 * mm
    total_w = card_w * 3 + 10 * mm * 2
    start_x = (PAGE_W - total_w) / 2
    y = PAGE_H - 150 * mm
    for i, (title, desc) in enumerate(cols):
        x = start_x + (card_w + 10 * mm) * i
        rounded(c, x, y, card_w, card_h, 4*mm,
                fill_color=BG_PINK, stroke_color=ROSE, lw=1.5)
        # アイコン円
        circle(c, x + card_w/2, y + card_h - 20*mm, 10*mm, fill_color=ROSE)
        label = ["LINE", "PC", "AUTO"][i]
        draw_text_in_box(c, x + card_w/2 - 10*mm, y + card_h - 30*mm,
                         20*mm, 20*mm, label,
                         font=FONT_B, size=12, color=WHITE, align='center', valign='middle')
        # タイトル
        draw_text(c, x + card_w/2, y + card_h - 42*mm, title,
                  font=FONT_B, size=20, color=DARK_ROSE, align='center')
        # 説明
        draw_text_in_box(c, x, y + 8*mm, card_w, 22*mm, desc,
                         font=FONT, size=12, color=BLACK, align='center', valign='middle')
    add_footer(c, 3)

def slide04(c):
    """3つの特徴"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "3つの特徴", 4)
    features = [
        ("01", "LINEから24時間予約（アプリ不要）",
         "お客様は普段お使いのLINEで、予約・変更・キャンセル・残回数確認がすべて完結。\n新しいアプリをダウンロードする必要はありません。"),
        ("02", "スマホ対応の管理画面",
         "オーナー様はスマホ・タブレット・PCから業務を確認・操作。\nお客様のご来店中でも、外出先でもスムーズに対応できます。"),
        ("03", "自動リマインド・自動バックアップ",
         "前日に自動でお客様へリマインドLINE。週次で自動バックアップ。\n「うっかり忘れ」も「データ消失」も、仕組みで防ぎます。"),
    ]
    top_y = PAGE_H - 42 * mm
    card_h = 38 * mm
    gap = 6 * mm
    for i, (no, title, body) in enumerate(features):
        y = top_y - (card_h + gap) * i - card_h
        rounded(c, 15*mm, y, PAGE_W - 30*mm, card_h, 4*mm,
                fill_color=BG_PINK, stroke_color=ROSE, lw=1.5)
        # 番号ブロック
        fill_rect(c, 15*mm, y, 35*mm, card_h, ROSE)
        # 左上下のラウンド処理は簡略 (直角でも装飾として成立)
        draw_text_in_box(c, 15*mm, y, 35*mm, card_h, no,
                         font=FONT_B, size=38, color=WHITE, align='center', valign='middle')
        # タイトル
        draw_text(c, 55*mm, y + card_h - 10*mm, title,
                  font=FONT_B, size=16, color=DARK_ROSE)
        # 本文
        draw_multiline(c, 55*mm, y + card_h - 15*mm, body,
                       font=FONT, size=11, color=BLACK, line_height=15)
    add_footer(c, 4)

def draw_phone(c, x, y, w, h, title, body_fn):
    """LINE風の端末モック"""
    # 外枠
    rounded(c, x, y, w, h, 3*mm, fill_color=LIGHT_GRAY, stroke_color=DARK_ROSE, lw=1.5)
    # 上部ヘッダ
    hdr_h = 8 * mm
    fill_rect(c, x + 2*mm, y + h - hdr_h - 2*mm, w - 4*mm, hdr_h, LINE_GREEN)
    draw_text_in_box(c, x + 2*mm, y + h - hdr_h - 2*mm, w - 4*mm, hdr_h,
                     title, font=FONT_B, size=10, color=WHITE, align='center', valign='middle')
    # 画面エリア
    scr_x = x + 2*mm
    scr_y = y + 2*mm
    scr_w = w - 4*mm
    scr_h = h - hdr_h - 4*mm
    fill_rect(c, scr_x, scr_y, scr_w, scr_h, WHITE)
    body_fn(c, scr_x, scr_y, scr_w, scr_h)

def slide05(c):
    """顧客体験①：LINEで予約完結"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "顧客体験1 LINEで予約完結", 5)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "お客様はLINEアプリひとつで、24時間いつでも予約できます。",
              font=FONT, size=13, color=DARK_ROSE)

    def body1(c, bx, by, bw, bh):
        # リッチメニュー風（2x3）
        btns = [("予約", ROSE), ("変更", GOLD), ("キャンセル", DARK_ROSE),
                ("残回数", ROSE), ("営業日", GOLD), ("お問合せ", DARK_ROSE)]
        btn_w = (bw - 8*mm) / 3
        btn_h = (bh - 15*mm) / 2
        draw_text(c, bx + bw/2, by + bh - 4*mm, "リッチメニュー",
                  font=FONT, size=8, color=GRAY, align='center')
        for i, (t, col) in enumerate(btns):
            r = i // 3; cc = i % 3
            bx2 = bx + 2*mm + (btn_w + 2*mm) * cc
            by2 = by + 2*mm + (btn_h + 2*mm) * (1 - r)
            rounded(c, bx2, by2, btn_w, btn_h, 2*mm, fill_color=col)
            draw_text_in_box(c, bx2, by2, btn_w, btn_h, t,
                             font=FONT_B, size=9, color=WHITE,
                             align='center', valign='middle')

    def body2(c, bx, by, bw, bh):
        # カレンダー
        draw_text(c, bx + bw/2, by + bh - 6*mm, "2026年4月",
                  font=FONT_B, size=10, color=DARK_ROSE, align='center')
        days = ['日','月','火','水','木','金','土']
        cw = bw / 7
        # 曜日行
        hdr_y = by + bh - 12*mm
        for i, d in enumerate(days):
            draw_text(c, bx + cw*i + cw/2, hdr_y, d,
                      font=FONT, size=7, color=GRAY, align='center')
        # 日付グリッド
        marks = [['o','x','o','o','-','o','o'],
                 ['o','o','x','o','o','-','o'],
                 ['-','o','o','x','o','o','o']]
        nums  = [['1','2','3','4','5','6','7'],
                 ['8','9','10','11','12','13','14'],
                 ['15','16','17','18','19','20','21']]
        for r in range(3):
            for ci in range(7):
                cx = bx + cw * ci + cw/2
                cy = hdr_y - 6*mm - r * 8*mm
                m = marks[r][ci]
                col = GREEN if m == 'o' else (RED if m == 'x' else GRAY)
                draw_text(c, cx, cy, nums[r][ci],
                          font=FONT, size=6, color=BLACK, align='center')
                draw_text(c, cx, cy - 3*mm, m,
                          font=FONT_B, size=9, color=col, align='center')

    def body3(c, bx, by, bw, bh):
        draw_text(c, bx + bw/2, by + bh - 6*mm, "4月8日（水）",
                  font=FONT_B, size=10, color=DARK_ROSE, align='center')
        times = [("10:00", False), ("11:00", False), ("13:00 OK", True),
                 ("14:00", False), ("15:00", False), ("16:00", False)]
        slot_h = 6 * mm
        gap = 1.5 * mm
        start_y = by + bh - 12*mm
        for i, (t, sel) in enumerate(times):
            y2 = start_y - (slot_h + gap) * (i + 1)
            fill_c = ROSE if sel else WHITE
            rounded(c, bx + 3*mm, y2, bw - 6*mm, slot_h, 1.5*mm,
                    fill_color=fill_c, stroke_color=ROSE, lw=0.75)
            draw_text_in_box(c, bx + 3*mm, y2, bw - 6*mm, slot_h, t,
                             font=FONT_B if sel else FONT, size=9,
                             color=(WHITE if sel else BLACK),
                             align='center', valign='middle')

    # 3つ並べる
    phone_w = 70 * mm
    phone_h = 100 * mm
    total = phone_w * 3 + 20 * mm * 2
    start_x = (PAGE_W - total) / 2
    phone_y = PAGE_H - 150 * mm
    titles = ["(1) メニューを開く", "(2) 日付を選ぶ", "(3) 時間を選んで確定"]
    bodies = [body1, body2, body3]
    centers = []
    for i in range(3):
        px = start_x + (phone_w + 20*mm) * i
        draw_phone(c, px, phone_y, phone_w, phone_h, titles[i], bodies[i])
        centers.append(px + phone_w)
    # 矢印
    for i in range(2):
        ax = centers[i] + 2*mm
        ay = phone_y + phone_h/2 - 4*mm
        right_arrow(c, ax, ay, 16*mm, 8*mm, ROSE)
    # 吹き出し
    cx = PAGE_W/2 - 60*mm
    cy = 18*mm
    rounded(c, cx, cy, 120*mm, 10*mm, 3*mm, fill_color=GOLD)
    draw_text_in_box(c, cx, cy, 120*mm, 10*mm,
                     "POINT  アプリをインストールする必要ナシ！",
                     font=FONT_B, size=13, color=WHITE, align='center', valign='middle')
    add_footer(c, 5)

def slide06(c):
    """顧客体験②"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "顧客体験2 予約変更・キャンセル・残回数確認", 6)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "お客様の「ちょっとした用件」も、LINEで完結します。",
              font=FONT, size=13, color=DARK_ROSE)
    items = [
        ("変更", "予約変更",
         "日時の変更がLINEから可能。\n予約確認メッセージの\n「変更する」ボタン1タップ。"),
        ("取消", "予約キャンセル",
         "急な用事でもLINEで即キャンセル。\nキャンセル料ポリシーも\n自動で事前表示。"),
        ("残数", "コース残回数",
         "「残回数」ボタンで現在の残数を\nいつでも確認。\n次回予約の目安にも。"),
    ]
    card_w = 90 * mm
    card_h = 88 * mm
    total = card_w * 3 + 10 * mm * 2
    start_x = (PAGE_W - total) / 2
    y = PAGE_H - 140*mm
    for i, (icon, t, d) in enumerate(items):
        x = start_x + (card_w + 10 * mm) * i
        rounded(c, x, y, card_w, card_h, 4*mm,
                fill_color=WHITE, stroke_color=ROSE, lw=2)
        # アイコン円
        cx = x + card_w/2
        cy = y + card_h - 20*mm
        circle(c, cx, cy, 12*mm, fill_color=BG_PINK, stroke_color=ROSE, lw=1.5)
        draw_text_in_box(c, cx - 12*mm, cy - 12*mm, 24*mm, 24*mm, icon,
                         font=FONT_B, size=16, color=ROSE,
                         align='center', valign='middle')
        # タイトル
        draw_text(c, cx, y + card_h - 42*mm, t,
                  font=FONT_B, size=18, color=DARK_ROSE, align='center')
        # 説明
        draw_text_in_box(c, x + 5*mm, y + 8*mm, card_w - 10*mm, 28*mm, d,
                         font=FONT, size=11, color=BLACK, align='center', valign='middle')
    # 結論バー
    rounded(c, 40*mm, 12*mm, PAGE_W - 80*mm, 12*mm, 3*mm, fill_color=ROSE)
    draw_text_in_box(c, 40*mm, 12*mm, PAGE_W - 80*mm, 12*mm,
                     "わざわざ電話する必要がない ＝ お客様の満足度UP",
                     font=FONT_B, size=14, color=WHITE, align='center', valign='middle')
    add_footer(c, 6)

def slide07(c):
    """オーナー体験①：ダッシュボード"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "オーナー体験1 ダッシュボード", 7)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "本日必要な情報が、ひと目でわかる画面設計。",
              font=FONT, size=13, color=DARK_ROSE)

    # ダッシュ全体枠
    dash_x = 15 * mm
    dash_y = 18 * mm
    dash_w = PAGE_W - 30 * mm
    dash_h = PAGE_H - 62 * mm
    rounded(c, dash_x, dash_y, dash_w, dash_h, 3*mm,
            fill_color=BG_PINK, stroke_color=ROSE, lw=2)
    # ヘッダ
    hdr_h = 10 * mm
    fill_rect(c, dash_x + 2*mm, dash_y + dash_h - hdr_h - 2*mm,
              dash_w - 4*mm, hdr_h, ROSE)
    draw_text(c, dash_x + 6*mm,
              dash_y + dash_h - hdr_h - 2*mm + hdr_h/2 - 2,
              "〇〇サロン  ダッシュボード",
              font=FONT_B, size=12, color=WHITE)
    draw_text(c, dash_x + dash_w - 6*mm,
              dash_y + dash_h - hdr_h - 2*mm + hdr_h/2 - 2,
              "2026/04/21 v", font=FONT, size=10, color=WHITE, align='right')

    # 統計4カード
    stats = [
        ("本日の予約", "5件",     ROSE),
        ("今月の売上", "¥482,000", GOLD),
        ("登録顧客数", "128名",   DARK_ROSE),
        ("要注意顧客", "3名",     ORANGE),
    ]
    card_top = dash_y + dash_h - 15*mm - 2
    card_h = 22 * mm
    card_gap = 3 * mm
    card_w = (dash_w - 6*mm - card_gap * 3) / 4
    for i, (t, v, col) in enumerate(stats):
        x = dash_x + 3*mm + (card_w + card_gap) * i
        y = card_top - card_h
        rounded(c, x, y, card_w, card_h, 2*mm,
                fill_color=WHITE, stroke_color=col, lw=1.5)
        draw_text(c, x + card_w/2, y + card_h - 6*mm, t,
                  font=FONT, size=9, color=GRAY, align='center')
        draw_text_in_box(c, x, y + 2*mm, card_w, card_h - 10*mm, v,
                         font=FONT_B, size=20, color=col, align='center', valign='middle')

    # 本日の予約リスト
    list_x = dash_x + 3*mm
    list_w = dash_w * 0.62
    list_h = 48 * mm
    list_y = dash_y + 3*mm
    rounded(c, list_x, list_y, list_w, list_h, 2*mm,
            fill_color=WHITE, stroke_color=LIGHT_PINK, lw=1)
    fill_rect(c, list_x, list_y + list_h - 8*mm, list_w, 8*mm, LIGHT_PINK)
    draw_text(c, list_x + 4*mm, list_y + list_h - 6*mm,
              "本日の予約", font=FONT_B, size=11, color=DARK_ROSE)
    rows = [
        ("10:00", "田中 美咲様",  "カット+カラー"),
        ("11:30", "佐藤 健一様",  "フェイシャル"),
        ("13:00", "鈴木 陽子様",  "コース (残3回)"),
        ("15:00", "高橋 由美様",  "カット"),
    ]
    row_h = 8 * mm
    for i, (tm, nm, mn) in enumerate(rows):
        yy = list_y + list_h - 12*mm - (row_h + 1*mm) * (i + 1)
        draw_text(c, list_x + 6*mm, yy + 2, tm,
                  font=FONT_B, size=10, color=ROSE)
        draw_text(c, list_x + 30*mm, yy + 2, nm, font=FONT, size=10, color=BLACK)
        draw_text(c, list_x + 80*mm, yy + 2, mn, font=FONT, size=10, color=GRAY)

    # 右サイド：バックアップ / 売上サマリー
    side_x = list_x + list_w + 3*mm
    side_w = dash_w - (side_x - dash_x) - 3*mm
    # バックアップ
    bu_h = 20 * mm
    bu_y = list_y + list_h - bu_h
    rounded(c, side_x, bu_y, side_w, bu_h, 2*mm,
            fill_color=WHITE, stroke_color=GREEN, lw=1.5)
    draw_text(c, side_x + 3*mm, bu_y + bu_h - 6*mm,
              "[OK] 最新バックアップ", font=FONT_B, size=11, color=GREEN)
    draw_multiline(c, side_x + 3*mm, bu_y + bu_h - 9*mm,
                   "2026/04/19 05:00\n（週次 毎週日曜5時）",
                   font=FONT, size=9, color=BLACK, line_height=11)
    # 売上サマリー
    sm_h = 24 * mm
    sm_y = list_y
    rounded(c, side_x, sm_y, side_w, sm_h, 2*mm,
            fill_color=WHITE, stroke_color=GOLD, lw=1.5)
    draw_text(c, side_x + 3*mm, sm_y + sm_h - 6*mm,
              "売上サマリー", font=FONT_B, size=11, color=DARK_ROSE)
    draw_multiline(c, side_x + 3*mm, sm_y + sm_h - 9*mm,
                   "今週: ¥128,500\n今月: ¥482,000\n前月比: +12%",
                   font=FONT, size=10, color=BLACK, line_height=12)
    add_footer(c, 7)

def slide08(c):
    """オーナー体験②：顧客管理・残回数"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "オーナー体験2 顧客管理・コース残回数", 8)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "残回数が少なくなったお客様を、自動でピックアップ。",
              font=FONT, size=13, color=DARK_ROSE)

    # 左：顧客テーブル
    tbl_x = 15 * mm
    tbl_y = 18 * mm
    tbl_w = PAGE_W * 0.62
    tbl_h = PAGE_H - 62 * mm
    rounded(c, tbl_x, tbl_y, tbl_w, tbl_h, 2*mm,
            fill_color=WHITE, stroke_color=ROSE, lw=1.5)
    # ヘッダ
    hdr_h = 8 * mm
    fill_rect(c, tbl_x, tbl_y + tbl_h - hdr_h, tbl_w, hdr_h, ROSE)
    draw_text(c, tbl_x + 4*mm, tbl_y + tbl_h - hdr_h + hdr_h/2 - 2,
              "顧客一覧", font=FONT_B, size=12, color=WHITE)
    # 列
    cols = [("顧客ID", 18*mm), ("お名前", 34*mm), ("コース", 50*mm),
            ("残回数", 22*mm), ("来店", 18*mm)]
    col_x = tbl_x + 3*mm
    # 列ヘッダ行
    hdr_row_y = tbl_y + tbl_h - hdr_h - 7*mm
    xp = col_x
    for h, w in cols:
        draw_text(c, xp + w/2, hdr_row_y, h,
                  font=FONT_B, size=9, color=DARK_ROSE, align='center')
        xp += w

    data = [
        ("C001", "田中 美咲",  "フェイシャル10回",  "8回",  GREEN,  "5回"),
        ("C002", "佐藤 健一",  "ボディケア5回",     "4回",  ORANGE, "2回"),
        ("C003", "鈴木 陽子",  "ヘアトリート10回",  "1回",  RED,    "8回"),
        ("C004", "高橋 由美",  "カラー5回",         "3回",  ORANGE, "3回"),
        ("C005", "山田 花子",  "コース終了",        "-",    GRAY,   "12回"),
        ("C006", "伊藤 明子",  "フェイシャル20回",  "15回", GREEN,  "6回"),
        ("C007", "渡辺 梨花",  "ボディケア10回",    "2回",  RED,    "9回"),
    ]
    row_h = 7 * mm
    start_y = hdr_row_y - 4*mm
    for i, (cid, nm, cs, rn, col_badge, vs) in enumerate(data):
        yy = start_y - (row_h + 0.5*mm) * (i + 1)
        if i % 2 == 0:
            fill_rect(c, tbl_x + 2*mm, yy, tbl_w - 4*mm, row_h, BG_PINK)
        xp = col_x
        # ID
        draw_text(c, xp + cols[0][1]/2, yy + row_h/2 - 2, cid,
                  font=FONT, size=9, color=DARK_ROSE, align='center')
        xp += cols[0][1]
        # 名前
        draw_text(c, xp + cols[1][1]/2, yy + row_h/2 - 2, nm,
                  font=FONT, size=10, color=BLACK, align='center')
        xp += cols[1][1]
        # コース
        draw_text(c, xp + cols[2][1]/2, yy + row_h/2 - 2, cs,
                  font=FONT, size=9, color=BLACK, align='center')
        xp += cols[2][1]
        # 残回数バッジ（円ピル）
        bw = 14*mm; bh = 5*mm
        bx = xp + (cols[3][1] - bw)/2
        by = yy + (row_h - bh)/2
        rounded(c, bx, by, bw, bh, bh/2, fill_color=col_badge)
        draw_text_in_box(c, bx, by, bw, bh, rn,
                         font=FONT_B, size=9, color=WHITE, align='center', valign='middle')
        xp += cols[3][1]
        # 来店
        draw_text(c, xp + cols[4][1]/2, yy + row_h/2 - 2, vs,
                  font=FONT, size=9, color=BLACK, align='center')

    # 右：要フォローアラート
    side_x = tbl_x + tbl_w + 5 * mm
    side_w = PAGE_W - side_x - 15*mm
    al_h = (tbl_h - 6*mm) / 2 - 3*mm
    al_y = tbl_y + tbl_h - al_h
    rounded(c, side_x, al_y, side_w, al_h, 3*mm, fill_color=RED)
    draw_text(c, side_x + side_w/2, al_y + al_h - 10*mm, "[注意] 要フォロー",
              font=FONT_B, size=16, color=WHITE, align='center')
    draw_text_in_box(c, side_x, al_y + 5*mm, side_w, al_h - 16*mm,
                     "残り4回以下の\nお客様が3名います。\n\nコース追加のご案内を\nお忘れなく！",
                     font=FONT, size=11, color=WHITE, align='center', valign='middle')

    # バッジ凡例
    lg_h = al_h
    lg_y = tbl_y
    rounded(c, side_x, lg_y, side_w, lg_h, 3*mm,
            fill_color=WHITE, stroke_color=ROSE, lw=1.5)
    draw_text(c, side_x + side_w/2, lg_y + lg_h - 8*mm, "バッジ色の見方",
              font=FONT_B, size=13, color=DARK_ROSE, align='center')
    legends = [("5回以上", GREEN,  "余裕あり"),
               ("2~4回",   ORANGE, "そろそろ案内"),
               ("1回以下", RED,    "要フォロー")]
    for i, (lv, cl, ls) in enumerate(legends):
        yy = lg_y + lg_h - 16*mm - i * 9*mm
        bw = 18*mm; bh = 6*mm
        rounded(c, side_x + 4*mm, yy, bw, bh, bh/2, fill_color=cl)
        draw_text_in_box(c, side_x + 4*mm, yy, bw, bh, lv,
                         font=FONT_B, size=8, color=WHITE,
                         align='center', valign='middle')
        draw_text(c, side_x + 4*mm + bw + 4*mm, yy + bh/2 - 2, ls,
                  font=FONT, size=10, color=BLACK)
    add_footer(c, 8)

def slide09(c):
    """オーナー体験③：売上レポート"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "オーナー体験3 売上レポート", 9)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "月別・日別の売上が、グラフで一目瞭然。CSVでダウンロードも可能。",
              font=FONT, size=13, color=DARK_ROSE)
    # 左：グラフ
    gx = 15*mm; gy = 18*mm
    gw = PAGE_W * 0.56
    gh = PAGE_H - 62*mm
    rounded(c, gx, gy, gw, gh, 2*mm,
            fill_color=WHITE, stroke_color=ROSE, lw=1.5)
    draw_text(c, gx + 4*mm, gy + gh - 7*mm, "月別売上（過去12ヶ月）",
              font=FONT_B, size=12, color=DARK_ROSE)
    # 棒グラフ
    months = ["5","6","7","8","9","10","11","12","1","2","3","4"]
    values = [0.45,0.52,0.48,0.55,0.6,0.65,0.7,0.82,0.58,0.62,0.75,0.88]
    chart_x = gx + 10*mm
    chart_y = gy + 10*mm
    chart_w = gw - 15*mm
    chart_h = gh - 25*mm
    bar_slots = 12
    bar_w = chart_w / (bar_slots * 1.4)
    gap = (chart_w - bar_w * bar_slots) / (bar_slots - 1)
    for i, (m, v) in enumerate(zip(months, values)):
        bh = chart_h * v
        bx = chart_x + (bar_w + gap) * i
        col = ROSE if v >= 0.8 else (GOLD if v >= 0.6 else LIGHT_PINK)
        fill_rect(c, bx, chart_y, bar_w, bh, col)
        draw_text(c, bx + bar_w/2, chart_y - 4*mm, m,
                  font=FONT, size=8, color=GRAY, align='center')
    # 軸ラベル
    draw_text(c, gx + 4*mm, chart_y + chart_h + 1*mm, "¥",
              font=FONT, size=9, color=GRAY)
    draw_text(c, gx + gw - 4*mm, chart_y - 7*mm, "月",
              font=FONT, size=9, color=GRAY, align='right')

    # 右：CSV風
    cx = gx + gw + 4*mm
    cwi = PAGE_W - cx - 15*mm
    ch = gh
    cy = gy
    rounded(c, cx, cy, cwi, ch, 2*mm,
            fill_color=WHITE, stroke_color=GOLD, lw=1.5)
    draw_text(c, cx + 4*mm, cy + ch - 7*mm, "支払い履歴ダウンロード",
              font=FONT_B, size=12, color=DARK_ROSE)
    # テーブル
    headers = ["日付", "顧客", "金額"]
    tblx = cx + 3*mm
    tbly_top = cy + ch - 14*mm
    tblw = cwi - 6*mm
    hdr_h = 6*mm
    fill_rect(c, tblx, tbly_top - hdr_h, tblw, hdr_h, ROSE)
    col_w = tblw / 3
    for i, h in enumerate(headers):
        draw_text_in_box(c, tblx + col_w*i, tbly_top - hdr_h, col_w, hdr_h, h,
                         font=FONT_B, size=9, color=WHITE,
                         align='center', valign='middle')
    rows = [("04/20","田中様","¥8,500"),
            ("04/20","佐藤様","¥12,000"),
            ("04/19","鈴木様","¥6,000"),
            ("04/19","高橋様","¥15,000"),
            ("04/18","山田様","¥8,500"),
            ("04/18","伊藤様","¥22,000"),
            ("04/17","渡辺様","¥8,500")]
    r_h = 6 * mm
    for ri, row in enumerate(rows):
        yy = tbly_top - hdr_h - r_h * (ri + 1)
        if ri % 2 == 0:
            fill_rect(c, tblx, yy, tblw, r_h, BG_PINK)
        for i, v in enumerate(row):
            draw_text_in_box(c, tblx + col_w*i, yy, col_w, r_h, v,
                             font=FONT, size=9, color=BLACK,
                             align='center', valign='middle')
    # DLボタン
    btn_w = cwi - 12*mm
    btn_h = 10*mm
    bx = cx + 6*mm
    by = cy + 5*mm
    rounded(c, bx, by, btn_w, btn_h, 2*mm, fill_color=GOLD)
    draw_text_in_box(c, bx, by, btn_w, btn_h, "CSVダウンロード",
                     font=FONT_B, size=12, color=WHITE,
                     align='center', valign='middle')
    add_footer(c, 9)

def slide10(c):
    """スマホ完全対応"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "スマホ完全対応", 10)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "PCでもスマホでも、画面サイズに合わせて自動で最適化。",
              font=FONT, size=13, color=DARK_ROSE)

    # 左：PC
    pc_x = 15*mm; pc_y = 22*mm
    pc_w = 140*mm; pc_h = PAGE_H - 70*mm
    rounded(c, pc_x, pc_y, pc_w, pc_h, 3*mm, fill_color=DARK)
    # 画面
    scr_margin = 6*mm
    scr_x = pc_x + scr_margin
    scr_y = pc_y + scr_margin
    scr_w = pc_w - scr_margin*2
    scr_h = pc_h - scr_margin*2
    fill_rect(c, scr_x, scr_y, scr_w, scr_h, WHITE)
    # ヘッダ
    hdr_h = 6*mm
    fill_rect(c, scr_x, scr_y + scr_h - hdr_h, scr_w, hdr_h, ROSE)
    # テーブル
    headers = ["日時", "顧客名", "メニュー", "金額"]
    col_w = scr_w / 4
    hdr_row_y = scr_y + scr_h - hdr_h - 6*mm
    for i, h in enumerate(headers):
        draw_text(c, scr_x + col_w*i + col_w/2, hdr_row_y + 2, h,
                  font=FONT_B, size=9, color=DARK_ROSE, align='center')
    pc_rows = [("4/21 10:00","田中様","カット","¥5,500"),
               ("4/21 11:30","佐藤様","カラー","¥12,000"),
               ("4/21 13:00","鈴木様","フェイシャル","¥8,000"),
               ("4/21 15:00","高橋様","コース","-")]
    for ri, row in enumerate(pc_rows):
        yy = hdr_row_y - 6*mm * (ri + 1)
        for i, v in enumerate(row):
            draw_text(c, scr_x + col_w*i + col_w/2, yy + 2, v,
                      font=FONT, size=8, color=BLACK, align='center')
    # スタンド
    fill_rect(c, pc_x + pc_w/2 - 12*mm, pc_y - 3*mm, 24*mm, 2*mm, DARK)
    fill_rect(c, pc_x + pc_w/2 - 20*mm, pc_y - 5*mm, 40*mm, 2*mm, DARK)
    draw_text(c, pc_x + pc_w/2, 12*mm, "PC：広々と一覧表示",
              font=FONT_B, size=12, color=DARK_ROSE, align='center')

    # 矢印中央
    ar_x = pc_x + pc_w + 8*mm
    ar_y = pc_y + pc_h/2 - 6*mm
    right_arrow(c, ar_x, ar_y, 30*mm, 12*mm, GOLD)
    draw_text_in_box(c, ar_x, ar_y, 30*mm, 12*mm, "自動切替",
                     font=FONT_B, size=11, color=WHITE, align='center', valign='middle')

    # 右：スマホ
    sp_x = pc_x + pc_w + 50*mm
    sp_y = pc_y + 5*mm
    sp_w = 60*mm; sp_h = pc_h - 10*mm
    rounded(c, sp_x, sp_y, sp_w, sp_h, 5*mm, fill_color=DARK)
    ssx = sp_x + 3*mm
    ssy = sp_y + 8*mm
    ssw = sp_w - 6*mm
    ssh = sp_h - 16*mm
    fill_rect(c, ssx, ssy, ssw, ssh, WHITE)
    # ヘッダ
    fill_rect(c, ssx, ssy + ssh - 6*mm, ssw, 6*mm, ROSE)
    draw_text_in_box(c, ssx, ssy + ssh - 6*mm, ssw, 6*mm, "予約一覧",
                     font=FONT_B, size=10, color=WHITE, align='center', valign='middle')
    # カード
    for r in range(4):
        yy = ssy + ssh - 6*mm - 18*mm - r * 17*mm
        rounded(c, ssx + 2*mm, yy, ssw - 4*mm, 15*mm, 2*mm,
                fill_color=BG_PINK, stroke_color=ROSE, lw=0.75)
        draw_text(c, ssx + 4*mm, yy + 10*mm,
                  f"4/21 {10 + r*2}:00",
                  font=FONT_B, size=9, color=DARK_ROSE)
        nms = ["田中様","佐藤様","鈴木様","高橋様"]
        mns = ["カット ¥5,500","カラー ¥12,000","フェイシャル ¥8,000","コース"]
        draw_text(c, ssx + 4*mm, yy + 6*mm, nms[r],
                  font=FONT, size=9, color=BLACK)
        draw_text(c, ssx + 4*mm, yy + 2*mm, mns[r],
                  font=FONT, size=8, color=GRAY)
    draw_text(c, sp_x + sp_w/2, 12*mm, "スマホ：カード型に自動変換",
              font=FONT_B, size=11, color=DARK_ROSE, align='center')
    add_footer(c, 10)

def slide11(c):
    """自動リマインド＆自動バックアップ"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "自動リマインド & 自動バックアップ", 11)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "「うっかり」と「もしもの時」から、サロンを守る仕組み。",
              font=FONT, size=13, color=DARK_ROSE)
    # 左：リマインド
    lx = 15*mm; ly = 16*mm
    lw = PAGE_W/2 - 20*mm
    lh = PAGE_H - 60*mm
    rounded(c, lx, ly, lw, lh, 3*mm,
            fill_color=BG_PINK, stroke_color=ROSE, lw=2)
    draw_text(c, lx + 4*mm, ly + lh - 8*mm, "前日リマインド",
              font=FONT_B, size=18, color=ROSE)
    draw_text(c, lx + 4*mm, ly + lh - 14*mm,
              "お客様のLINEに自動でメッセージ",
              font=FONT, size=11, color=DARK_ROSE)
    # 吹き出し
    bx = lx + 6*mm; bh = 42*mm
    bw = lw - 12*mm
    by = ly + lh - 18*mm - bh
    rounded(c, bx, by, bw, bh, 3*mm,
            fill_color=WHITE, stroke_color=GRAY, lw=0.75)
    draw_multiline(c, bx + 4*mm, by + bh - 3*mm,
                   "〇〇サロンです\n\n明日 4/22（金）14:00 から\nカット+カラーのご予約を\nお待ちしております。\n\n変更・キャンセルはメニューから。",
                   font=FONT, size=11, color=BLACK, line_height=14)
    # 効果
    eff_y = ly + 5*mm; eff_h = 18*mm
    rounded(c, lx + 6*mm, eff_y, lw - 12*mm, eff_h, 3*mm, fill_color=GREEN)
    draw_text(c, lx + lw/2, eff_y + eff_h - 6*mm, "効果",
              font=FONT_B, size=11, color=WHITE, align='center')
    draw_text(c, lx + lw/2, eff_y + 5*mm,
              "無断キャンセル激減 → 機会損失を防止",
              font=FONT_B, size=13, color=WHITE, align='center')

    # 右：バックアップ
    rx = PAGE_W/2 + 5*mm; ry = ly
    rw = PAGE_W/2 - 20*mm; rh = lh
    rounded(c, rx, ry, rw, rh, 3*mm,
            fill_color=BG_PINK, stroke_color=GOLD, lw=2)
    draw_text(c, rx + 4*mm, ry + rh - 8*mm, "週次バックアップ",
              font=FONT_B, size=18, color=GOLD)
    draw_text(c, rx + 4*mm, ry + rh - 14*mm,
              "毎週日曜5時、自動でデータを保管",
              font=FONT, size=11, color=DARK_ROSE)
    # スケジュール
    sched = [("日","5:00",True),("月","",False),("火","",False),
             ("水","",False),("木","",False),("金","",False),("土","",False)]
    sw = (rw - 16*mm) / 7
    sy = ry + rh - 35*mm
    for i, (d, tm, active) in enumerate(sched):
        x = rx + 4*mm + sw * i + 1*mm
        col = ROSE if active else LIGHT_GRAY
        rounded(c, x, sy, sw - 2*mm, 14*mm, 2*mm, fill_color=col)
        draw_text(c, x + (sw-2*mm)/2, sy + 10*mm, d,
                  font=FONT_B, size=10, color=(WHITE if active else GRAY), align='center')
        if tm:
            draw_text(c, x + (sw-2*mm)/2, sy + 4*mm, tm,
                      font=FONT_B, size=8, color=WHITE, align='center')
    # 状態
    draw_text(c, rx + 4*mm, sy - 5*mm,
              "→ ダッシュボードに「最新バックアップ」表示",
              font=FONT, size=10, color=BLACK)
    st_y = sy - 14*mm
    rounded(c, rx + 6*mm, st_y, rw - 12*mm, 7*mm, 2*mm,
            fill_color=WHITE, stroke_color=GREEN, lw=1.5)
    draw_text_in_box(c, rx + 6*mm, st_y, rw - 12*mm, 7*mm,
                     "[OK] 2026/04/19 05:00 バックアップ完了",
                     font=FONT_B, size=11, color=GREEN,
                     align='center', valign='middle')
    # 効果
    eff2_y = ry + 5*mm; eff2_h = 18*mm
    rounded(c, rx + 6*mm, eff2_y, rw - 12*mm, eff2_h, 3*mm, fill_color=GOLD)
    draw_text_in_box(c, rx + 6*mm, eff2_y, rw - 12*mm, eff2_h,
                     "データ消失の心配なし\nいつでも過去30日分から復元可能",
                     font=FONT_B, size=12, color=WHITE,
                     align='center', valign='middle')
    add_footer(c, 11)

def slide12(c):
    """セキュリティ対策"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "セキュリティ対策", 12)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "大切なお客様情報を、しっかり守る4つの仕組み。",
              font=FONT, size=13, color=DARK_ROSE)
    items = [
        ("鍵", "パスワードはハッシュ化保存",
         "万一データが見られても\nパスワードは復元不可能な\n形で保管されます。"),
        ("暗号", "通信は暗号化",
         "LINE・管理画面とサーバー間の\nすべての通信を暗号化。\n盗聴される心配はありません。"),
        ("ユーザ", "共有PCでも安心",
         "ログイン情報は保存せず、\nブラウザを閉じれば自動ログアウト。\n店舗の共用PCでも使えます。"),
        ("記録", "全操作ログ記録",
         "「誰がいつ何をしたか」を\n自動で記録。\nトラブル時の追跡が可能です。"),
    ]
    # 2x2 レイアウト
    card_w = (PAGE_W - 40*mm) / 2
    card_h = (PAGE_H - 62*mm) / 2 - 2*mm
    for i, (icon, title, desc) in enumerate(items):
        r = i // 2; cc = i % 2
        x = 15*mm + (card_w + 10*mm) * cc
        y = PAGE_H - 42*mm - card_h - (card_h + 4*mm) * r
        rounded(c, x, y, card_w, card_h, 3*mm,
                fill_color=WHITE, stroke_color=ROSE, lw=1.5)
        # アイコン円
        icy = y + card_h - 17*mm
        circle(c, x + 14*mm, icy, 9*mm, fill_color=ROSE)
        draw_text_in_box(c, x + 5*mm, icy - 9*mm, 18*mm, 18*mm, icon,
                         font=FONT_B, size=12, color=WHITE,
                         align='center', valign='middle')
        # タイトル
        draw_text(c, x + 28*mm, y + card_h - 10*mm, title,
                  font=FONT_B, size=15, color=DARK_ROSE)
        # 本文
        draw_multiline(c, x + 28*mm, y + card_h - 16*mm, desc,
                       font=FONT, size=11, color=BLACK, line_height=14)
    add_footer(c, 12)

def slide13(c):
    """他システムとの違い（テーブル）"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "他システムとの違い", 13)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "コスト・柔軟性・データ所有権。すべてサロン側のメリットを追求。",
              font=FONT, size=13, color=DARK_ROSE)
    rows = [
        ["項目", "当システム", "大手予約サイト"],
        ["月額固定費", "要相談（変動なし）", "高額 ＋ 手数料"],
        ["LINE連携", "標準搭載", "オプション"],
        ["カスタマイズ（店舗名・文言・料金）", "自由に変更可", "制限あり"],
        ["データ所有", "サロン側", "事業者側"],
        ["予約手数料", "なし", "1件ごとに課金"],
    ]
    # 表描画
    tbl_x = 25*mm
    tbl_w = PAGE_W - 50*mm
    tbl_y_top = PAGE_H - 48*mm
    col_widths = [tbl_w * 0.34, tbl_w * 0.33, tbl_w * 0.33]
    hdr_h = 12*mm
    row_h = 14*mm
    tbl_h = hdr_h + row_h * (len(rows) - 1)
    # ヘッダ
    fill_rect(c, tbl_x, tbl_y_top - hdr_h, tbl_w, hdr_h, ROSE)
    xp = tbl_x
    for i, h in enumerate(rows[0]):
        draw_text_in_box(c, xp, tbl_y_top - hdr_h, col_widths[i], hdr_h, h,
                         font=FONT_B, size=14, color=WHITE,
                         align='center', valign='middle')
        xp += col_widths[i]
    # 行
    for ri, row in enumerate(rows[1:]):
        yy = tbl_y_top - hdr_h - row_h * (ri + 1)
        # 背景色（偶数白、奇数極薄ピンク）
        base_c = BG_PINK if ri % 2 == 0 else WHITE
        fill_rect(c, tbl_x, yy, tbl_w, row_h, base_c)
        xp = tbl_x
        for ci, val in enumerate(row):
            # 項目列は薄ピンク背景
            if ci == 0:
                fill_rect(c, xp, yy, col_widths[ci], row_h, LIGHT_PINK)
                col = DARK_ROSE
                fnt = FONT_B
            elif ci == 1:
                col = ROSE
                fnt = FONT_B
            else:
                col = GRAY
                fnt = FONT
            draw_text_in_box(c, xp + 2*mm, yy, col_widths[ci] - 4*mm, row_h, val,
                             font=fnt, size=13, color=col,
                             align='center', valign='middle')
            xp += col_widths[ci]
        # 行境界線
        c.setStrokeColor(LIGHT_GRAY); c.setLineWidth(0.3)
        c.line(tbl_x, yy, tbl_x + tbl_w, yy)
    # 外枠
    stroke_rect(c, tbl_x, tbl_y_top - tbl_h, tbl_w, tbl_h, ROSE, 0.8)

    draw_text(c, 15*mm, 14*mm,
              "※ 上記は一般的な比較です。具体的な金額・条件は個別にご相談ください。",
              font=FONT, size=9, color=GRAY)
    add_footer(c, 13)

def slide14(c):
    """導入の流れ（4週間）"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "導入の流れ（4週間）", 14)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "お申込みから運用開始まで、およそ4週間で完了します。",
              font=FONT, size=13, color=DARK_ROSE)
    weeks = [
        ("Week 1", "ヒアリング & 環境準備",
         "サロン様の業務フローをお伺いし、\nGoogleアカウント・LINE公式アカウント\nの準備をサポート。"),
        ("Week 2", "LINE公式アカウント連携",
         "予約メニュー・リッチメニューの設定、\nサロン専用の挨拶メッセージや\nキャンセルポリシーを登録。"),
        ("Week 3", "初期データ移行・動作確認",
         "既存顧客データの取り込み、\nメニュー・コース料金の登録、\nテスト予約での動作確認。"),
        ("Week 4", "運用開始 & 操作研修",
         "オンライン研修（管理画面・\nよくある操作）を実施。\n本格運用スタート後もサポート継続。"),
    ]
    card_w = (PAGE_W - 30*mm - 18*mm) / 4
    card_h = 90*mm
    arrow_w = 6*mm
    y = PAGE_H - 130*mm
    for i, (wk, ttl, dsc) in enumerate(weeks):
        x = 15*mm + (card_w + arrow_w) * i
        # 番号円（上）
        cxc = x + card_w/2
        cyc = y + card_h + 10*mm
        circle(c, cxc, cyc, 8*mm, fill_color=ROSE, stroke_color=GOLD, lw=2.5)
        draw_text_in_box(c, cxc - 8*mm, cyc - 8*mm, 16*mm, 16*mm, str(i + 1),
                         font=FONT_B, size=22, color=WHITE,
                         align='center', valign='middle')
        # カード
        rounded(c, x, y, card_w, card_h, 3*mm,
                fill_color=WHITE, stroke_color=ROSE, lw=1.5)
        # Week ラベル
        draw_text(c, x + card_w/2, y + card_h - 10*mm, wk,
                  font=FONT_B, size=13, color=GOLD, align='center')
        # タイトル
        draw_text_in_box(c, x, y + card_h - 22*mm, card_w, 10*mm, ttl,
                         font=FONT_B, size=12, color=DARK_ROSE,
                         align='center', valign='middle')
        # 説明
        draw_text_in_box(c, x + 3*mm, y + 5*mm, card_w - 6*mm, card_h - 35*mm,
                         dsc,
                         font=FONT, size=10, color=BLACK,
                         align='center', valign='middle', line_height=13)
        # 矢印
        if i < 3:
            right_arrow(c, x + card_w + 1*mm, y + card_h/2 - 3*mm,
                        arrow_w - 2*mm, 6*mm, GOLD)

    draw_text(c, 15*mm, 14*mm,
              "※ サロン様のご都合やデータ量により、期間は前後する場合があります。",
              font=FONT, size=9, color=GRAY)
    add_footer(c, 14)

def slide15(c):
    """料金プラン"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "料金プラン", 15)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "サロン様の規模・ご要望に合わせて、個別にお見積もりいたします。",
              font=FONT, size=13, color=DARK_ROSE)
    plans = [
        ("INIT", "初期費用", "要相談",
         "・環境構築・初期設定\n・LINE公式アカウント連携\n・既存データ移行\n・オンライン研修1回"),
        ("MONTH", "月額保守費", "要相談",
         "・システム稼働監視\n・データバックアップ\n・LINE・メールサポート\n・軽微な修正対応"),
        ("OPT", "オプション", "要相談",
         "・カスタマイズ開発\n・追加研修\n・繁忙期サポート強化\n・複数店舗対応"),
    ]
    card_w = 90*mm
    card_h = 115*mm
    total_w = card_w * 3 + 10*mm * 2
    start_x = (PAGE_W - total_w) / 2
    y = 18*mm
    for i, (icon, ttl, pr, dsc) in enumerate(plans):
        x = start_x + (card_w + 10*mm) * i
        mid = (i == 1)
        fill_c = ROSE if mid else WHITE
        text_c = WHITE if mid else DARK_ROSE
        price_c = WHITE if mid else ROSE
        desc_c = WHITE if mid else BLACK
        rounded(c, x, y, card_w, card_h, 4*mm,
                fill_color=fill_c, stroke_color=ROSE, lw=2)
        # アイコンラベル
        draw_text(c, x + card_w/2, y + card_h - 15*mm, icon,
                  font=FONT_B, size=18, color=(WHITE if mid else GOLD), align='center')
        # タイトル
        draw_text(c, x + card_w/2, y + card_h - 30*mm, ttl,
                  font=FONT_B, size=18, color=text_c, align='center')
        # 区切り
        line_c = WHITE if mid else GOLD
        fill_rect(c, x + 15*mm, y + card_h - 38*mm, card_w - 30*mm, 0.6*mm, line_c)
        # 価格
        draw_text(c, x + card_w/2, y + card_h - 55*mm, pr,
                  font=FONT_B, size=28, color=price_c, align='center')
        # 説明
        draw_multiline(c, x + 8*mm, y + card_h - 68*mm, dsc,
                       font=FONT, size=11, color=desc_c, line_height=15)
    # 注記
    note_y = 8*mm
    rounded(c, 50*mm, note_y, PAGE_W - 100*mm, 9*mm, 2*mm, fill_color=BG_PINK)
    draw_text_in_box(c, 50*mm, note_y, PAGE_W - 100*mm, 9*mm,
                     "※ 個別見積もりいたします。お気軽にご相談ください。",
                     font=FONT_B, size=11, color=DARK_ROSE,
                     align='center', valign='middle')
    add_footer(c, 15)

def slide16(c):
    """サポート体制"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "サポート体制", 16)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "導入後も安心の4段階サポート。困った時はいつでもご相談ください。",
              font=FONT, size=13, color=DARK_ROSE)
    supports = [
        ("1", "導入時", "設定代行 + オンライン研修",
         "初期設定を代行し、管理画面の操作方法を\nオンライン（画面共有）で丁寧にご説明。"),
        ("2", "運用開始後", "LINE・メールサポート",
         "ご不明点はLINEまたはメールで\n24時間受付。営業日に順次回答します。"),
        ("3", "月次", "運用状況の確認",
         "月1回、予約件数・売上・稼働状況を\nレポートとしてご報告。改善提案も。"),
        ("4", "緊急時", "障害対応",
         "システム停止や重大な不具合発生時は\n優先対応。復旧までの情報共有も密に。"),
    ]
    card_w = (PAGE_W - 40*mm) / 2
    card_h = (PAGE_H - 62*mm) / 2 - 2*mm
    for i, (icon, when, what, desc) in enumerate(supports):
        r = i // 2; cc = i % 2
        x = 15*mm + (card_w + 10*mm) * cc
        y = PAGE_H - 42*mm - card_h - (card_h + 4*mm) * r
        rounded(c, x, y, card_w, card_h, 3*mm,
                fill_color=BG_PINK, stroke_color=ROSE, lw=1.5)
        # アイコン円
        cxc = x + 12*mm
        cyc = y + card_h/2
        circle(c, cxc, cyc, 8*mm, fill_color=GOLD)
        draw_text_in_box(c, cxc - 8*mm, cyc - 8*mm, 16*mm, 16*mm, icon,
                         font=FONT_B, size=18, color=WHITE,
                         align='center', valign='middle')
        # when
        draw_text(c, x + 25*mm, y + card_h - 8*mm, when,
                  font=FONT_B, size=11, color=GOLD)
        # what
        draw_text(c, x + 25*mm, y + card_h - 15*mm, what,
                  font=FONT_B, size=14, color=DARK_ROSE)
        # desc
        draw_multiline(c, x + 25*mm, y + card_h - 22*mm, desc,
                       font=FONT, size=11, color=BLACK, line_height=14)
    add_footer(c, 16)

def slide17(c):
    """よくあるご質問"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "よくあるご質問", 17)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "導入前によくいただくご質問をまとめました。",
              font=FONT, size=12, color=DARK_ROSE)
    qas = [
        ("操作が難しそうで不安です。",
         "ご心配いりません。導入時にマニュアルをお渡しし、オンライン研修で実際に操作しながらご説明します。運用開始後もいつでも質問OK。"),
        ("データはどこに保管されますか？",
         "Google社のクラウド（Googleドライブ）上に、オーナー様のアカウントで保管されます。データの所有権は完全にサロン様にあります。"),
        ("既存の顧客データはどうなりますか？",
         "エクセル・CSVで書き出せる形式であれば、一括でインポートできます。移行作業は弊社で代行しますのでご安心ください。"),
        ("途中で解約したくなったら？",
         "データはそのまま保持され、サロン様のGoogleアカウントに残ります。いつでも内容を確認・ダウンロードしていただけます。"),
        ("月の予約件数に制限はありますか？",
         "システム自体に件数上限はありません。LINE公式アカウントの無料枠を超える規模の場合は、有料プランへの移行をご相談いたします。"),
    ]
    top_y = PAGE_H - 46*mm
    block_h = 22 * mm
    for i, (q, a) in enumerate(qas):
        y = top_y - block_h * (i + 1)
        # Q
        qbox = 8 * mm
        rounded(c, 15*mm, y + block_h - qbox - 1*mm, qbox, qbox, 1.5*mm, fill_color=ROSE)
        draw_text_in_box(c, 15*mm, y + block_h - qbox - 1*mm, qbox, qbox, "Q",
                         font=FONT_B, size=13, color=WHITE,
                         align='center', valign='middle')
        draw_text(c, 26*mm, y + block_h - qbox + 1*mm, q,
                  font=FONT_B, size=13, color=DARK_ROSE)
        # A
        rounded(c, 15*mm, y + 1*mm, qbox, qbox, 1.5*mm, fill_color=GOLD)
        draw_text_in_box(c, 15*mm, y + 1*mm, qbox, qbox, "A",
                         font=FONT_B, size=13, color=WHITE,
                         align='center', valign='middle')
        draw_multiline(c, 26*mm, y + qbox + 1*mm, a,
                       font=FONT, size=10, color=BLACK, line_height=13)
    add_footer(c, 17)

def slide18(c):
    """お客様の声"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "お客様の声", 18)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "導入いただいたサロン様からのコメントをご紹介します。",
              font=FONT, size=13, color=DARK_ROSE)
    voices = [
        ("A", "サロンA様（ヘアサロン）",
         "導入1ヶ月で、無断キャンセルが\n半分以下に減りました。\n前日リマインドの効果は絶大です。",
         "★★★★★"),
        ("B", "サロンB様（エステ）",
         "お客様から『LINEで予約できて\n便利』と好評。新規のご予約も\n月30％増加しました。",
         "★★★★★"),
        ("C", "サロンC様（ネイル）",
         "残回数が可視化されたことで、\nコース追加のご案内が\n自然にできるようになりました。",
         "★★★★★"),
    ]
    card_w = 90*mm
    card_h = 110*mm
    total_w = card_w * 3 + 10*mm * 2
    start_x = (PAGE_W - total_w) / 2
    y = 22*mm
    for i, (icon, who, body, stars) in enumerate(voices):
        x = start_x + (card_w + 10*mm) * i
        rounded(c, x, y, card_w, card_h, 3*mm,
                fill_color=WHITE, stroke_color=ROSE, lw=2)
        # アイコン円
        cxc = x + card_w/2
        cyc = y + card_h - 20*mm
        circle(c, cxc, cyc, 12*mm, fill_color=BG_PINK, stroke_color=ROSE, lw=1.5)
        draw_text_in_box(c, cxc - 12*mm, cyc - 12*mm, 24*mm, 24*mm, icon,
                         font=FONT_B, size=24, color=ROSE,
                         align='center', valign='middle')
        # 星
        draw_text(c, cxc, y + card_h - 42*mm, stars,
                  font=FONT, size=14, color=GOLD, align='center')
        # サロン名
        draw_text(c, cxc, y + card_h - 52*mm, who,
                  font=FONT_B, size=12, color=DARK_ROSE, align='center')
        # コメント
        quoted = "「" + body + "」"
        draw_text_in_box(c, x + 5*mm, y + 5*mm, card_w - 10*mm, 38*mm, quoted,
                         font=FONT, size=11, color=BLACK,
                         align='center', valign='middle', line_height=15)
    draw_text(c, PAGE_W/2, 11*mm,
              "※ 上記はイメージです。実際の導入事例は、ご要望に応じて個別にご紹介いたします。",
              font=FONT, size=9, color=GRAY, align='center')
    add_footer(c, 18)

def slide19(c):
    """導入までの次のステップ"""
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, WHITE)
    add_title_bar(c, "導入までの次のステップ", 19)
    draw_text(c, 15*mm, PAGE_H - 38*mm,
              "たった5ステップで、新しいサロン運営が始まります。",
              font=FONT, size=13, color=DARK_ROSE)
    steps = [
        ("1", "本資料ご確認", "まずはこの資料をゆっくりご確認ください。"),
        ("2", "ヒアリング（30分無料）",
         "オンラインまたは訪問で、現状の課題をお伺いします。"),
        ("3", "お見積り提示",
         "サロン様に最適なプラン・金額をご提案。"),
        ("4", "ご契約・初期設定",
         "ご契約後、4週間で環境構築・データ移行を実施。"),
        ("5", "運用開始",
         "操作研修を経て、本格運用スタート！"),
    ]
    tl_x = 40 * mm
    # 縦線
    top_y = PAGE_H - 46*mm
    bot_y = 22*mm
    fill_rect(c, tl_x - 0.5*mm, bot_y, 1*mm, top_y - bot_y, GOLD)
    step_h = (top_y - bot_y) / 5
    for i, (no, ttl, dsc) in enumerate(steps):
        y = top_y - step_h * (i + 1) + 3*mm
        # 円
        cy = y + step_h/2 - 2*mm
        circle(c, tl_x, cy, 7*mm, fill_color=ROSE, stroke_color=WHITE, lw=2)
        draw_text_in_box(c, tl_x - 7*mm, cy - 7*mm, 14*mm, 14*mm, no,
                         font=FONT_B, size=18, color=WHITE,
                         align='center', valign='middle')
        # カード
        cx = tl_x + 12*mm
        cwidth = PAGE_W - cx - 15*mm
        ch = step_h - 4*mm
        cypos = y
        rounded(c, cx, cypos, cwidth, ch, 2*mm,
                fill_color=BG_PINK, stroke_color=ROSE, lw=1)
        draw_text(c, cx + 4*mm, cypos + ch/2 - 2, ttl,
                  font=FONT_B, size=13, color=DARK_ROSE)
        draw_text(c, cx + 70*mm, cypos + ch/2 - 2, dsc,
                  font=FONT, size=11, color=BLACK)
    add_footer(c, 19)

def slide20(c):
    """連絡先"""
    # 背景極薄ピンク
    fill_rect(c, 0, 0, PAGE_W, PAGE_H, BG_PINK)
    fill_rect(c, 0, PAGE_H - 6*mm, PAGE_W, 6*mm, ROSE)
    fill_rect(c, 0, 0, PAGE_W, 6*mm, ROSE)
    # メインコピー
    draw_text(c, PAGE_W/2, PAGE_H - 30*mm, "まずはお気軽にご相談ください",
              font=FONT_B, size=32, color=DARK_ROSE, align='center')
    draw_text(c, PAGE_W/2, PAGE_H - 44*mm, "Contact Us",
              font=FONT, size=16, color=GOLD, align='center')
    # 中央カード
    cx = 70*mm
    cy = 28*mm
    cw = PAGE_W - 140*mm
    ch = PAGE_H - 86*mm
    rounded(c, cx, cy, cw, ch, 5*mm,
            fill_color=WHITE, stroke_color=ROSE, lw=3)
    # 担当者ラベル
    draw_text(c, PAGE_W/2, cy + ch - 15*mm, "担当者",
              font=FONT, size=10, color=GRAY, align='center')
    draw_text(c, PAGE_W/2, cy + ch - 25*mm, "〇〇 〇〇",
              font=FONT_B, size=22, color=DARK_ROSE, align='center')
    # 区切り
    fill_rect(c, cx + 30*mm, cy + ch - 35*mm, cw - 60*mm, 0.5*mm, GOLD)
    # メール
    draw_text(c, PAGE_W/2, cy + ch - 45*mm, "Email",
              font=FONT_B, size=11, color=ROSE, align='center')
    draw_text(c, PAGE_W/2, cy + ch - 54*mm, "xxxxx@example.com",
              font=FONT, size=18, color=BLACK, align='center')
    # 電話
    draw_text(c, PAGE_W/2, cy + ch - 68*mm, "TEL",
              font=FONT_B, size=11, color=ROSE, align='center')
    draw_text(c, PAGE_W/2, cy + ch - 77*mm, "000-0000-0000",
              font=FONT, size=18, color=BLACK, align='center')
    # 営業時間
    draw_text(c, PAGE_W/2, cy + 8*mm, "営業時間: 平日 10:00〜18:00",
              font=FONT, size=10, color=GRAY, align='center')
    # Thank you
    draw_text(c, PAGE_W/2, 12*mm, "Thank you",
              font=FONT_B, size=16, color=ROSE, align='center')


# ================================================================
# メイン
# ================================================================
def main():
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "SALON_PROPOSAL.pdf")
    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("サロン顧客管理システム ご提案資料")
    c.setAuthor("Salon Customer Management System")

    slides = [
        slide01, slide02, slide03, slide04, slide05,
        slide06, slide07, slide08, slide09, slide10,
        slide11, slide12, slide13, slide14, slide15,
        slide16, slide17, slide18, slide19, slide20,
    ]
    for fn in slides:
        fn(c)
        c.showPage()
    c.save()
    size = os.path.getsize(out_path)
    print(f"Saved: {out_path}")
    print(f"Size: {size} bytes ({size/1024:.1f} KB)")
    print(f"Slides: {len(slides)}")

if __name__ == "__main__":
    main()
