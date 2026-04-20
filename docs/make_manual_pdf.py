"""
Generate OWNER_SETUP_MANUAL.pdf from OWNER_SETUP_MANUAL.md using reportlab.

- Japanese font: Meiryo (meiryo.ttc / meiryob.ttc) on Windows
- Emoji font: Segoe UI Emoji (seguiemj.ttf) as fallback for emoji glyphs
- Code font: Consolas
- Output: A4, cover page, TOC, styled headings, step banners, callouts, tables, checklists, page numbers
"""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Flowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

# ------------------------------------------------------------
# Fonts
# ------------------------------------------------------------
FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont("Meiryo", f"{FONT_DIR}/meiryo.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("MeiryoBold", f"{FONT_DIR}/meiryob.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("Consolas", f"{FONT_DIR}/consola.ttf"))
pdfmetrics.registerFont(TTFont("ConsolasBold", f"{FONT_DIR}/consolab.ttf"))

# Try to register emoji font; reportlab can only use it as a separate font,
# so we fall back to "replace emojis in text" approach for simplicity.
try:
    pdfmetrics.registerFont(TTFont("SegoeEmoji", f"{FONT_DIR}/seguiemj.ttf"))
    HAS_EMOJI = True
except Exception:
    HAS_EMOJI = False

from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Meiryo", normal="Meiryo", bold="MeiryoBold",
                   italic="Meiryo", boldItalic="MeiryoBold")

# ------------------------------------------------------------
# Colors
# ------------------------------------------------------------
ROSE_PINK = colors.HexColor("#D4688A")
DARK_PINK = colors.HexColor("#7B4A5C")
LIGHT_PINK_BG = colors.HexColor("#FFF0F3")
STEP_BANNER_BG = colors.HexColor("#F9D5E0")

WARN_BORDER = colors.HexColor("#E53935")
WARN_BG = colors.HexColor("#FFEBEE")
TIP_BORDER = colors.HexColor("#1976D2")
TIP_BG = colors.HexColor("#E3F2FD")
IMPORTANT_BORDER = colors.HexColor("#2E7D32")
IMPORTANT_BG = colors.HexColor("#E8F5E9")

CODE_BG = colors.HexColor("#F5F5F5")
CODE_BORDER = colors.HexColor("#CCCCCC")

# ------------------------------------------------------------
# Styles
# ------------------------------------------------------------
BASE_FONT = "Meiryo"
BOLD_FONT = "MeiryoBold"

styles = {
    "Title": ParagraphStyle(
        "Title", fontName=BOLD_FONT, fontSize=28, leading=38,
        textColor=ROSE_PINK, alignment=TA_CENTER, spaceAfter=24,
    ),
    "CoverSub": ParagraphStyle(
        "CoverSub", fontName=BASE_FONT, fontSize=12, leading=22,
        textColor=colors.black, alignment=TA_CENTER, spaceAfter=8,
    ),
    "H1": ParagraphStyle(
        "H1", fontName=BOLD_FONT, fontSize=18, leading=24,
        textColor=ROSE_PINK, spaceBefore=18, spaceAfter=10,
        borderPadding=2, underlineWidth=1, underlineColor=ROSE_PINK,
    ),
    "H2": ParagraphStyle(
        "H2", fontName=BOLD_FONT, fontSize=14, leading=20,
        textColor=DARK_PINK, spaceBefore=12, spaceAfter=6,
    ),
    "H3": ParagraphStyle(
        "H3", fontName=BOLD_FONT, fontSize=12, leading=18,
        textColor=DARK_PINK, spaceBefore=8, spaceAfter=4,
    ),
    "Body": ParagraphStyle(
        "Body", fontName=BASE_FONT, fontSize=10.5, leading=17,
        textColor=colors.black, spaceAfter=5,
    ),
    "BodyIndent": ParagraphStyle(
        "BodyIndent", fontName=BASE_FONT, fontSize=10.5, leading=17,
        textColor=colors.black, leftIndent=14, spaceAfter=4,
    ),
    "List": ParagraphStyle(
        "List", fontName=BASE_FONT, fontSize=10.5, leading=17,
        textColor=colors.black, leftIndent=14, bulletIndent=2, spaceAfter=2,
    ),
    "CheckList": ParagraphStyle(
        "CheckList", fontName=BASE_FONT, fontSize=10.5, leading=17,
        textColor=colors.black, leftIndent=14, spaceAfter=2,
    ),
    "Code": ParagraphStyle(
        "Code", fontName="Consolas", fontSize=9.5, leading=14,
        textColor=colors.black, leftIndent=6, rightIndent=6,
        backColor=CODE_BG, borderColor=CODE_BORDER, borderWidth=0.5,
        borderPadding=6, spaceBefore=4, spaceAfter=8,
    ),
    "Callout": ParagraphStyle(
        "Callout", fontName=BASE_FONT, fontSize=10.5, leading=17,
        textColor=colors.black,
    ),
    "StepBanner": ParagraphStyle(
        "StepBanner", fontName=BOLD_FONT, fontSize=22, leading=30,
        textColor=colors.white, alignment=TA_LEFT,
        backColor=ROSE_PINK, borderPadding=8, spaceBefore=16, spaceAfter=12,
    ),
    "TOC": ParagraphStyle(
        "TOC", fontName=BASE_FONT, fontSize=11, leading=18, textColor=colors.black,
    ),
    "TOCTitle": ParagraphStyle(
        "TOCTitle", fontName=BOLD_FONT, fontSize=18, leading=24,
        textColor=ROSE_PINK, spaceAfter=12, alignment=TA_CENTER,
    ),
    "Footer": ParagraphStyle(
        "Footer", fontName=BASE_FONT, fontSize=9, textColor=colors.grey,
        alignment=TA_CENTER,
    ),
}

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")

def md_inline_to_html(text: str) -> str:
    """Convert Markdown inline syntax (**bold**, `code`) to reportlab HTML tags."""
    # Escape XML-hostile chars first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = BOLD_RE.sub(r"<b>\1</b>", text)
    # Inline code
    text = INLINE_CODE_RE.sub(
        r'<font face="Consolas" backColor="#F5F5F5">\1</font>', text
    )
    return text


class HR(Flowable):
    """Horizontal rule."""
    def __init__(self, width, thickness=0.5, color=colors.lightgrey):
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.color = color

    def wrap(self, *args):
        return (self.width, self.thickness + 4)

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 2, self.width, 2)


def make_callout(lines, kind="tip"):
    """Render a callout box (tip/warn/important) as a single-cell table."""
    if kind == "warn":
        border, bg = WARN_BORDER, WARN_BG
    elif kind == "important":
        border, bg = IMPORTANT_BORDER, IMPORTANT_BG
    else:
        border, bg = TIP_BORDER, TIP_BG

    body = "<br/>".join(lines)
    p = Paragraph(body, styles["Callout"])
    tbl = Table([[p]], colWidths=[170 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 1, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tbl


def make_code_block(code_text):
    """Render a code block as a table with grey background."""
    # Preserve line breaks, escape HTML
    safe = (code_text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace(" ", "&nbsp;"))
    safe = safe.replace("\n", "<br/>")
    p = Paragraph(f'<font face="Consolas" size="9.5">{safe}</font>', styles["Body"])
    tbl = Table([[p]], colWidths=[170 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, CODE_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def make_table(header, rows):
    """Build a Markdown table with pink header row."""
    data = [header] + rows
    # Convert each cell's markdown inline to Paragraph so wrapping works
    styled = []
    for r_idx, row in enumerate(data):
        new_row = []
        for cell in row:
            txt = md_inline_to_html(cell)
            style = styles["Body"] if r_idx > 0 else ParagraphStyle(
                "TH", parent=styles["Body"], fontName=BOLD_FONT)
            new_row.append(Paragraph(txt, style))
        styled.append(new_row)

    ncols = len(header)
    # Distribute widths
    total = 170 * mm
    col_widths = [total / ncols] * ncols

    tbl = Table(styled, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_PINK_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl


# ------------------------------------------------------------
# Markdown parser
# ------------------------------------------------------------
STEP_RE = re.compile(r"^Step\s+(\d+):\s*(.+)$")

def parse_markdown(md_text):
    """Very small Markdown->flowables converter tailored for this document."""
    lines = md_text.split("\n")
    flowables = []

    i = 0
    n = len(lines)
    # Skip the very first H1 (handled on cover), first top-blockquote, and TOC section
    # Cover/TOC are built separately. Skip until the first real section:
    # "## 1. はじめに" (anything before that, incl. the MD TOC, is dropped).
    while i < n and not lines[i].startswith("## 1. "):
        i += 1

    while i < n:
        line = lines[i]

        # Horizontal rule
        if line.strip() == "---":
            flowables.append(Spacer(1, 6))
            flowables.append(HR(170 * mm))
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # Code block
        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            flowables.append(make_code_block("\n".join(buf)))
            continue

        # Table (header line has `|` and next line is separator)
        if line.startswith("|") and i + 1 < n and re.match(r"^\|[\s\-:|]+\|$", lines[i+1]):
            header_cells = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            flowables.append(make_table(header_cells, rows))
            flowables.append(Spacer(1, 6))
            continue

        # H2 heading — could be "## Step N: ..." banner, or "## 1. ..." etc.
        if line.startswith("## "):
            heading = line[3:].strip()
            m = STEP_RE.match(heading)
            if m:
                # Step banner
                flowables.append(PageBreak())
                num, title = m.group(1), m.group(2)
                banner = Paragraph(f"Step {num}: {title}", styles["StepBanner"])
                flowables.append(banner)
            else:
                flowables.append(Paragraph(md_inline_to_html(heading), styles["H1"]))
                # underline effect via HR
                flowables.append(HR(170 * mm, thickness=1, color=ROSE_PINK))
                flowables.append(Spacer(1, 4))
            i += 1
            continue

        # H3 heading
        if line.startswith("### "):
            heading = line[4:].strip()
            flowables.append(Paragraph(md_inline_to_html(heading), styles["H2"]))
            i += 1
            continue

        # H4 heading
        if line.startswith("#### "):
            heading = line[5:].strip()
            flowables.append(Paragraph(md_inline_to_html(heading), styles["H3"]))
            i += 1
            continue

        # Blockquote (callout)
        if line.startswith("> "):
            buf = []
            kind = "tip"
            while i < n and (lines[i].startswith("> ") or lines[i].strip() == ">"):
                content = lines[i][2:] if lines[i].startswith("> ") else ""
                buf.append(content)
                i += 1
            # Detect kind
            joined = " ".join(buf)
            if "⚠️" in joined or "注意" in joined[:20]:
                kind = "warn"
            elif "🎯" in joined or "重要" in joined[:10]:
                kind = "important"
            else:
                kind = "tip"
            rendered_lines = [md_inline_to_html(b) for b in buf if b.strip() or True]
            # Collapse empty lines
            rendered_lines = [l if l.strip() else "&nbsp;" for l in rendered_lines]
            flowables.append(make_callout(rendered_lines, kind=kind))
            flowables.append(Spacer(1, 6))
            continue

        # Checklist item: - [ ] or - [x]
        m = re.match(r"^\s*-\s*\[([ xX])\]\s*(.+)$", line)
        if m:
            checked = m.group(1).lower() == "x"
            text = m.group(2)
            mark = "\u2611" if checked else "\u2610"  # ☑ / ☐
            flowables.append(Paragraph(f"{mark} {md_inline_to_html(text)}", styles["CheckList"]))
            i += 1
            continue

        # Ordered list
        m = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
        if m:
            flowables.append(Paragraph(
                f"{m.group(1)}. {md_inline_to_html(m.group(2))}", styles["List"]))
            i += 1
            continue

        # Unordered list
        m = re.match(r"^\s*-\s+(.+)$", line)
        if m:
            flowables.append(Paragraph(
                f"• {md_inline_to_html(m.group(1))}", styles["List"]))
            i += 1
            continue

        # Blank line
        if not line.strip():
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Italic single-line "_..._" (last-updated footer-like)
        m = re.match(r"^_(.+)_$", line.strip())
        if m:
            flowables.append(Paragraph(
                f"<i>{md_inline_to_html(m.group(1))}</i>", styles["Body"]))
            i += 1
            continue

        # Regular paragraph
        flowables.append(Paragraph(md_inline_to_html(line), styles["Body"]))
        i += 1

    return flowables


# ------------------------------------------------------------
# Cover & TOC
# ------------------------------------------------------------
def build_cover():
    items = []
    items.append(Spacer(1, 60 * mm))
    items.append(Paragraph("サロン顧客管理システム", styles["Title"]))
    items.append(Paragraph("セットアップガイド", styles["Title"]))
    items.append(Spacer(1, 20 * mm))
    items.append(Paragraph("対象: サロンオーナー様", styles["CoverSub"]))
    items.append(Paragraph("バージョン: v77", styles["CoverSub"]))
    items.append(Paragraph("読了目安: 約2〜3時間", styles["CoverSub"]))
    items.append(Spacer(1, 40 * mm))
    items.append(Paragraph("Happy Salon Life 💐", styles["CoverSub"]))
    items.append(PageBreak())
    return items


def build_toc():
    items = [Paragraph("目次", styles["TOCTitle"]), Spacer(1, 8)]
    entries = [
        ("1. はじめに", ""),
        ("2. 事前準備", ""),
        ("Step 1: Googleスプレッドシートをコピーする", ""),
        ("Step 2: LINE公式アカウントを作る", ""),
        ("Step 3: GAS（プログラム）を自分用に設定する", ""),
        ("Step 4: ウェブアプリとして公開する（デプロイ）", ""),
        ("Step 5: LINEのWebhook設定", ""),
        ("Step 6: 初期化スクリプトを実行する", ""),
        ("Step 7: リッチメニューを設定する", ""),
        ("Step 8: 管理画面にログインしてみる", ""),
        ("Step 9: テスト予約をしてみる", ""),
        ("Step 10: 定期トリガーをセットする", ""),
        ("日常運用ガイド", ""),
        ("こんなとき どうする（FAQ）", ""),
        ("困ったら連絡先", ""),
    ]
    data = [[Paragraph(t, styles["TOC"]), Paragraph("", styles["TOC"])] for t, _ in entries]
    tbl = Table(data, colWidths=[150 * mm, 20 * mm])
    tbl.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    items.append(tbl)
    items.append(PageBreak())
    return items


# ------------------------------------------------------------
# Page number footer
# ------------------------------------------------------------
def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(BASE_FONT, 9)
    canvas.setFillColor(colors.grey)
    page_num_text = f"- {doc.page} -"
    canvas.drawCentredString(A4[0] / 2.0, 10 * mm, page_num_text)
    canvas.restoreState()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    md_path = r"C:\Users\Owner\Documents\salon-repo\docs\OWNER_SETUP_MANUAL.md"
    pdf_path = r"C:\Users\Owner\Documents\salon-repo\docs\OWNER_SETUP_MANUAL.pdf"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
        title="サロン顧客管理システム セットアップガイド",
    )

    flowables = []
    flowables.extend(build_cover())
    flowables.extend(build_toc())
    flowables.extend(parse_markdown(md_text))

    doc.build(flowables, onFirstPage=draw_footer, onLaterPages=draw_footer)
    print(f"Generated: {pdf_path}")
    print(f"Size: {os.path.getsize(pdf_path):,} bytes")


if __name__ == "__main__":
    main()
