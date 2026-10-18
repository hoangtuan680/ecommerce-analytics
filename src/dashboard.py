"""Bảng điều khiển đa khung hình 2x2 bằng Matplotlib."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

COLORS = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"]
_million = FuncFormatter(lambda v, _: f"{v / 1e6:,.0f}")


def _style(ax, title):
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=10)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def build_dashboard(monthly, city, category, kpi, out_path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    (ax1, ax2), (ax3, ax4) = axes
    x = range(len(monthly))
    ticks = list(x)[::3]
    labels = monthly.index[::3]

    # 1) Xu hướng doanh thu theo thời gian
    ax1.plot(x, monthly["revenue"], color=COLORS[0], lw=2.2, marker="o", ms=3)
    ax1.fill_between(x, monthly["revenue"], alpha=0.12, color=COLORS[0])
    ax1.set_xticks(ticks, labels, rotation=45, ha="right")
    ax1.yaxis.set_major_formatter(_million)
    ax1.set_ylabel("Triệu VND")
    _style(ax1, "Xu hướng doanh thu theo tháng")

    # 2) Tỷ trọng theo thành phố
    ax2.pie(city, labels=city.index, autopct="%1.1f%%", startangle=90, colors=COLORS,
            wedgeprops={"width": 0.42, "edgecolor": "white"}, pctdistance=0.79,
            textprops={"fontsize": 9})
    ax2.set_title("Tỷ trọng doanh thu theo thành phố", fontsize=12, fontweight="bold", loc="left", pad=10)

    # 3) Phân rã theo danh mục
    ax3.barh(category.index[::-1], category.values[::-1], color=COLORS[1])
    ax3.xaxis.set_major_formatter(_million)
    ax3.set_xlabel("Triệu VND")
    _style(ax3, "Doanh thu theo danh mục sản phẩm")
    ax3.grid(axis="x", alpha=0.25)
    ax3.grid(axis="y", visible=False)

    # 4) Giá trị đơn hàng trung bình
    ax4.plot(x, monthly["aov"], color=COLORS[2], lw=2.2, marker="o", ms=3)
    ax4.axhline(kpi["aov"], color="gray", ls="--", lw=1)
    ax4.set_xticks(ticks, labels, rotation=45, ha="right")
    ax4.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e3:,.0f}k"))
    ax4.set_ylabel("VND / đơn")
    _style(ax4, "Giá trị đơn hàng trung bình (AOV)")

    fig.suptitle(
        f"DASHBOARD DOANH SỐ  |  Tổng doanh thu: {kpi['total_revenue'] / 1e9:,.2f} tỷ ₫  |  "
        f"Số đơn: {kpi['orders']:,}  |  AOV: {kpi['aov']:,.0f} ₫",
        fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
