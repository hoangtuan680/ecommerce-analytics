"""Tiền xử lý dữ liệu và tính các chỉ số kinh doanh."""
from __future__ import annotations

import pandas as pd

CANONICAL_CITIES = ["TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]
_CITY_LOOKUP = {c.lower(): c for c in CANONICAL_CITIES}


def load_raw(path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["order_date"])


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Làm sạch dữ liệu: bỏ trùng, bỏ đơn hủy, chuẩn hóa text, tạo thuộc tính thời gian."""
    report = {"Số dòng ban đầu": len(raw)}

    df = raw.drop_duplicates().copy()
    report["Dòng trùng lặp bị loại"] = len(raw) - len(df)

    df["status"] = df["status"].astype(str).str.strip().str.title()
    report["Đơn bị hủy bị loại"] = int((df["status"] == "Cancelled").sum())
    df = df.loc[df["status"] == "Completed"].copy()

    n = len(df)
    df = df.dropna(subset=["quantity", "unit_price"]).copy()
    report["Dòng thiếu giá/số lượng bị loại"] = n - len(df)

    df["city"] = (
        df["city"].str.strip().str.replace(r"\s+", " ", regex=True).str.lower()
        .map(_CITY_LOOKUP).fillna("Khác")
    )

    # Thuộc tính thời gian + doanh thu
    df["Year"] = df["order_date"].dt.year
    df["Month"] = df["order_date"].dt.month
    df["YearMonth"] = df["order_date"].dt.strftime("%Y-%m")
    df["revenue"] = df["quantity"] * df["unit_price"]

    df = df.sort_values("order_date").reset_index(drop=True)
    report["Số dòng sau làm sạch"] = len(df)
    return df, report


def kpis(df: pd.DataFrame) -> dict:
    total = df["revenue"].sum()
    orders = df["order_id"].nunique()
    return {
        "total_revenue": total,
        "orders": orders,
        "aov": total / orders,  # Giá trị đơn hàng trung bình
        "customers": df["customer_id"].nunique(),
    }


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    m = df.groupby("YearMonth").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
    m["aov"] = m["revenue"] / m["orders"]
    return m


def revenue_by(df: pd.DataFrame, col: str) -> pd.Series:
    return df.groupby(col)["revenue"].sum().sort_values(ascending=False)


def fmt_vnd(v: float) -> str:
    if v >= 1e9:
        return f"{v / 1e9:,.2f} tỷ ₫"
    if v >= 1e6:
        return f"{v / 1e6:,.1f} triệu ₫"
    return f"{v:,.0f} ₫"
