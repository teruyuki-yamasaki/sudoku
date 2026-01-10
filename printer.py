import os
import json
from reportlab.lib.pagesizes import A4, A5
from reportlab.pdfgen import canvas

# ===== config =====
CELL = 28
GRID = CELL * 9

DEFAULT_MARGIN_X = 40
DEFAULT_MARGIN_Y = 60
TITLE_OFFSET_Y = 10

def draw_grid(c, x, y, cell=CELL, base_width=1):
    size = cell * 9
    for i in range(10):
        w = base_width * 2 if i % 3 == 0 else base_width
        c.setLineWidth(w)
        c.line(x, y + i * cell, x + size, y + i * cell)
        c.line(x + i * cell, y, x + i * cell, y + size)

def draw_numbers(c, grid_str, x, y, cell=CELL,
                 font="Helvetica", size=16):
    c.setFont(font, size)
    for i, ch in enumerate(grid_str):
        if ch != ".":
            r = 8 - i // 9
            col = i % 9
            c.drawCentredString(
                x + col * cell + cell / 2,
                y + r * cell + cell / 2 - 4,
                ch
            )

def draw_title(c, text, x, y,
               font="Helvetica-Bold", size=14):
    c.setFont(font, size)
    c.drawString(x, y, text)

def layout_single_page(page_size):
    """
    1ページ1問用レイアウト
    """
    x = DEFAULT_MARGIN_X
    y = page_size[1] - GRID - DEFAULT_MARGIN_Y
    title_y = y + GRID + TITLE_OFFSET_Y
    return [{
        "grid_x": x,
        "grid_y": y,
        "title_x": x,
        "title_y": title_y
    }]

def layout_two_per_page(page_size):
    """
    1ページに縦2問配置
    """
    page_w, page_h = page_size

    x = DEFAULT_MARGIN_X

    # 上段
    y_top = page_h - GRID - DEFAULT_MARGIN_Y
    title_y_top = y_top + GRID + TITLE_OFFSET_Y

    # 下段（少し余白を空ける）
    gap = 40
    y_bottom = y_top - GRID - gap
    title_y_bottom = y_bottom + GRID + TITLE_OFFSET_Y

    return [
        {
            "grid_x": x,
            "grid_y": y_top,
            "title_x": x,
            "title_y": title_y_top
        },
        {
            "grid_x": x,
            "grid_y": y_bottom,
            "title_x": x,
            "title_y": title_y_bottom
        }
    ]

def layout_nxm(page_size, n_rows, m_cols,
               margin_x=DEFAULT_MARGIN_X,
               margin_y=DEFAULT_MARGIN_Y,
               gap_x=20,
               gap_y=40):
    """
    1ページに n_rows × m_cols 問配置
    """
    page_w, page_h = page_size

    blocks = []

    total_width = m_cols * GRID + (m_cols - 1) * gap_x
    total_height = n_rows * GRID + (n_rows - 1) * gap_y

    start_x = margin_x
    start_y = page_h - margin_y - GRID

    if start_x + total_width > page_w:
        raise ValueError("横方向にページサイズを超えています")

    if start_y - (total_height - GRID) < 0:
        raise ValueError("縦方向にページサイズを超えています")

    for row in range(n_rows):
        for col in range(m_cols):
            x = start_x + col * (GRID + gap_x)
            y = start_y - row * (GRID + gap_y)
            title_y = y + GRID + TITLE_OFFSET_Y

            blocks.append({
                "grid_x": x,
                "grid_y": y,
                "title_x": x,
                "title_y": title_y
            })

    return blocks

def layout_nxm_centered(
    page_size,
    n_rows,
    m_cols,
    gap_x=40,
    gap_y=40,
):
    """
    1ページ n×m 問を中央揃えで配置
    """
    page_w, page_h = page_size

    blocks = []

    total_w = m_cols * GRID + (m_cols - 1) * gap_x
    total_h = n_rows * GRID + (n_rows - 1) * gap_y

    if total_w > page_w or total_h > page_h:
        raise ValueError("レイアウトがページサイズを超えています")

    # ⭐ 中央寄せの肝
    start_x = (page_w - total_w) / 2
    start_y = (page_h + total_h) / 2 - GRID

    for row in range(n_rows):
        for col in range(m_cols):
            x = start_x + col * (GRID + gap_x)
            y = start_y - row * (GRID + gap_y)

            blocks.append({
                "grid_x": x,
                "grid_y": y,
                "title_x": x,
                "title_y": y + GRID + TITLE_OFFSET_Y
            })

    return blocks

def layout_nxm_maximized(
    page_size,
    n_rows,
    m_cols,
    margin_x=40,
    margin_y=60,
    gap_x=20,
    gap_y=40,
):
    """
    n×m に合わせて盤面を最大サイズで中央配置
    """
    page_w, page_h = page_size

    # ページ内で使える最大サイズ
    usable_w = page_w - 2 * margin_x - (m_cols - 1) * gap_x
    usable_h = page_h - 2 * margin_y - (n_rows - 1) * gap_y - TITLE_OFFSET_Y

    # 1問あたりの最大 GRID サイズ
    grid_w = usable_w / m_cols
    grid_h = usable_h / n_rows

    # GRID = CELL * 9
    cell = min(grid_w, grid_h) / 9
    cell = int(cell)  # ピクセル単位で丸める

    grid = cell * 9

    total_w = m_cols * grid + (m_cols - 1) * gap_x
    total_h = n_rows * grid + (n_rows - 1) * gap_y

    start_x = (page_w - total_w) / 2
    start_y = (page_h + total_h) / 2 - grid

    blocks = []

    for r in range(n_rows):
        for c in range(m_cols):
            x = start_x + c * (grid + gap_x)
            y = start_y - r * (grid + gap_y)

            blocks.append({
                "grid_x": x,
                "grid_y": y,
                "title_x": x,
                "title_y": y + grid + TITLE_OFFSET_Y,
                "cell": cell,
            })

    return blocks


def load_puzzles_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_puzzles(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def make_pdf(
    puzzles,
    pdf_path,
    page_size=A5,
    layout_func=lambda s: layout_nxm_centered(s, 2, 1),
    show_solution=False,
):
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    c = canvas.Canvas(pdf_path, pagesize=page_size)

    layout = layout_func(page_size)
    per_page = len(layout)

    problem_no = 1
    i = 0

    while i < len(puzzles):
        for block in layout:
            if i >= len(puzzles):
                break

            p = puzzles[i]

            title = f"No.{problem_no}  Level: {p['difficulty']}"
            draw_title(
                c, title,
                block["title_x"],
                block["title_y"]
            )

            draw_grid(
                c,
                block["grid_x"],
                block["grid_y"]
            )

            grid_data = p["solution"] if show_solution else p["puzzle"]
            draw_numbers(
                c,
                grid_data,
                block["grid_x"],
                block["grid_y"]
            )

            i += 1
            problem_no += 1

        c.showPage()

    c.save()


if __name__ == "__main__":
    from generator import PRESETS
    from exporter import Config

    cfg = Config()
    for diffculty in PRESETS.keys():
        cfg.diff = str(diffculty)
        puzzles = load_puzzles_json(cfg.json_path)
        puzzles = puzzles[:cfg.n_problems_printout]
        make_pdf(
            puzzles,
            pdf_path=cfg.problems_pdf,
            show_solution=False
        )
        make_pdf(
            puzzles,
            pdf_path=cfg.answers_pdf,
            show_solution=True
        )
        print("✔ 問題集・解答集PDF生成完了")
