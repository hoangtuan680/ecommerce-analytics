"""Sinh báo cáo HTML với đồ họa vector thuần (SVG) - không phụ thuộc ảnh bitmap.

Mọi biểu đồ được vẽ bằng chuỗi SVG (path/line/rect/text) nên luôn sắc nét
ở mọi độ phân giải, mở trực tiếp bằng trình duyệt.
"""
from __future__ import annotations

import html
import math
from datetime import datetime

from .analysis import fmt_vnd

PALETTE = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"]
W, H = 560, 300


def _open():
    return f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img">'


def svg_line(labels, values, color, fmt):
    pl, pr, pt, pb = 58, 16, 16, 46
    iw, ih = W - pl - pr, H - pt - pb
    vmax = max(values) * 1.1
    X = lambda i: pl + iw * i / (len(values) - 1)
    Y = lambda v: pt + ih * (1 - v / vmax)
    p = [_open()]
    for k in range(5):
        v = vmax * k / 4
        p.append(f'<line x1="{pl}" x2="{W - pr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/>')
        p.append(f'<text x="{pl - 8}" y="{Y(v) + 4:.1f}" class="tick" text-anchor="end">{fmt(v)}</text>')
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(values))
    p.append(f'<polygon points="{pl},{Y(0):.1f} {pts} {X(len(values) - 1):.1f},{Y(0):.1f}" fill="{color}" opacity="0.12"/>')
    p.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round"/>')
    for i, lab in enumerate(labels):
        if i % 3 == 0:
            p.append(f'<text x="{X(i):.1f}" y="{H - pb + 18}" class="tick" text-anchor="middle">{html.escape(lab)}</text>')
    p.append("</svg>")
    return "".join(p)


def svg_donut(labels, values):
    cx, cy, R, r = 150, 150, 110, 66
    total = sum(values)
    angle = -math.pi / 2
    p = [_open()]
    for i, (lab, v) in enumerate(zip(labels, values)):
        frac = v / total
        a2 = angle + 2 * math.pi * frac
        large = 1 if frac > 0.5 else 0
        pt = lambda rad, a: (cx + rad * math.cos(a), cy + rad * math.sin(a))
        x1, y1 = pt(R, angle); x2, y2 = pt(R, a2)
        x3, y3 = pt(r, a2); x4, y4 = pt(r, angle)
        d = (f"M{x1:.2f},{y1:.2f} A{R},{R} 0 {large} 1 {x2:.2f},{y2:.2f} "
             f"L{x3:.2f},{y3:.2f} A{r},{r} 0 {large} 0 {x4:.2f},{y4:.2f} Z")
        color = PALETTE[i % len(PALETTE)]
        p.append(f'<path d="{d}" fill="{color}" stroke="var(--card)" stroke-width="2"/>')
        ly = 70 + i * 32
        p.append(f'<rect x="320" y="{ly - 11}" width="14" height="14" rx="3" fill="{color}"/>')
        p.append(f'<text x="342" y="{ly}" class="label">{html.escape(lab)}</text>')
        p.append(f'<text x="{W - 12}" y="{ly}" class="label" text-anchor="end" font-weight="600">{frac * 100:.1f}%</text>')
        angle = a2
    p.append(f'<text x="{cx}" y="{cy + 5}" class="label" text-anchor="middle" font-weight="600">Theo thành phố</text>')
    p.append("</svg>")
    return "".join(p)


def svg_bars(labels, values, fmt):
    pl, pr, pt = 100, 90, 12
    bh = (H - pt - 12) / len(values)
    vmax = max(values)
    p = [_open()]
    for i, (lab, v) in enumerate(zip(labels, values)):
        y = pt + i * bh
        bw = (W - pl - pr) * v / vmax
        p.append(f'<text x="{pl - 10}" y="{y + bh / 2 + 4:.1f}" class="label" text-anchor="end">{html.escape(lab)}</text>')
        p.append(f'<rect x="{pl}" y="{y + bh * 0.18:.1f}" width="{bw:.1f}" height="{bh * 0.64:.1f}" rx="4" fill="{PALETTE[1]}"/>')
        p.append(f'<text x="{pl + bw + 8:.1f}" y="{y + bh / 2 + 4:.1f}" class="tick">{fmt(v)}</text>')
    p.append("</svg>")
    return "".join(p)


CSS = """
:root{--bg:#f4f5f9;--card:#fff;--text:#1f2937;--muted:#6b7280;--grid:#e5e7eb}
@media (prefers-color-scheme:dark){:root{--bg:#0f1117;--card:#1a1d27;--text:#e5e7eb;--muted:#9ca3af;--grid:#2d3142}}
*{box-sizing:border-box}
body{margin:0;padding:24px;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1100px;margin:auto}
h1{font-size:1.5rem;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 20px;font-size:.9rem}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:14px}
.kpi,.card{background:var(--card);border-radius:14px;padding:16px 18px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.kpi span{display:block;color:var(--muted);font-size:.8rem}.kpi b{font-size:1.4rem}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:14px}
.card h2{font-size:1rem;margin:0 0 8px}
svg{width:100%;height:auto;display:block}
.grid{stroke:var(--grid);stroke-width:1}.tick{fill:var(--muted);font-size:11px}.label{fill:var(--text);font-size:13px}
"""


def build_report(monthly, city, category, kpi, out_path):
    k = lambda v: f"{v / 1e6:,.0f}tr"
    cards = [
        ("Xu hướng doanh thu theo tháng (triệu ₫)", svg_line(list(monthly.index), list(monthly["revenue"]), PALETTE[0], k)),
        ("Tỷ trọng doanh thu theo thành phố", svg_donut(list(city.index), list(city.values))),
        ("Doanh thu theo danh mục sản phẩm", svg_bars(list(category.index), list(category.values), fmt_vnd)),
        ("Giá trị đơn hàng trung bình (AOV)", svg_line(list(monthly.index), list(monthly["aov"]), PALETTE[2], lambda v: f"{v / 1e3:,.0f}k")),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><span>{t}</span><b>{v}</b></div>' for t, v in [
            ("Tổng doanh thu", fmt_vnd(kpi["total_revenue"])),
            ("Số đơn hoàn tất", f"{kpi['orders']:,}"),
            ("Giá trị đơn trung bình", fmt_vnd(kpi["aov"])),
            ("Số khách hàng", f"{kpi['customers']:,}"),
        ])
    card_html = "".join(f'<div class="card"><h2>{t}</h2>{s}</div>' for t, s in cards)
    doc = f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Báo cáo doanh số thương mại điện tử</title><style>{CSS}</style></head>
<body><div class="wrap">
<h1>Báo cáo doanh số thương mại điện tử</h1>
<p class="sub">Tự động sinh bởi Python · {datetime.now():%d/%m/%Y %H:%M} · Đồ họa vector SVG</p>
<div class="kpis">{kpi_html}</div>
<div class="grid2">{card_html}</div>
</div></body></html>"""
    out_path.write_text(doc, encoding="utf-8")
