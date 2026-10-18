"""Chạy toàn bộ luồng: sinh dữ liệu -> làm sạch -> tính chỉ số -> dashboard -> báo cáo SVG/HTML."""
from pathlib import Path

from src.analysis import clean, fmt_vnd, kpis, load_raw, monthly_summary, revenue_by
from src.dashboard import build_dashboard
from src.generate_data import generate
from src.svg_report import build_report

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw" / "orders.csv"
CLEAN = ROOT / "data" / "processed" / "orders_clean.csv"
OUT = ROOT / "output"


def main():
    for p in (RAW.parent, CLEAN.parent, OUT):
        p.mkdir(parents=True, exist_ok=True)

    if not RAW.exists():
        generate().to_csv(RAW, index=False)
        print(f"Đã sinh dữ liệu mô phỏng -> {RAW.relative_to(ROOT)}")

    df, report = clean(load_raw(RAW))
    df.to_csv(CLEAN, index=False)
    print("\n== Báo cáo làm sạch ==")
    for key, val in report.items():
        print(f"  {key}: {val:,}")

    kpi = kpis(df)
    print("\n== Chỉ số cốt lõi ==")
    print(f"  Tổng doanh thu: {fmt_vnd(kpi['total_revenue'])}")
    print(f"  Giá trị đơn hàng trung bình (AOV): {fmt_vnd(kpi['aov'])}")

    monthly = monthly_summary(df)
    city, category = revenue_by(df, "city"), revenue_by(df, "category")

    build_dashboard(monthly, city, category, kpi, OUT / "dashboard.png")
    build_report(monthly, city, category, kpi, OUT / "report.html")
    print("\nĐã xuất: output/dashboard.png, output/report.html")


if __name__ == "__main__":
    main()
