"""Sinh bộ dữ liệu thương mại điện tử mô phỏng (có chứa dữ liệu nhiễu)."""
from __future__ import annotations

import numpy as np
import pandas as pd

CITY_WEIGHTS = {
    "TP. Hồ Chí Minh": 0.38,
    "Hà Nội": 0.28,
    "Đà Nẵng": 0.12,
    "Cần Thơ": 0.12,
    "Hải Phòng": 0.10,
}

# danh mục: (tỷ lệ đơn, giá trung vị VND)
CATEGORIES = {
    "Điện tử": (0.20, 2_500_000),
    "Thời trang": (0.30, 350_000),
    "Gia dụng": (0.20, 600_000),
    "Mỹ phẩm": (0.15, 280_000),
    "Sách": (0.15, 120_000),
}

# Hệ số mùa vụ: Tết (T2 thấp), 9.9 / 11.11 / 12.12 (T9-T12 cao)
SEASON = {1: 1.05, 2: 0.85, 3: 0.95, 4: 0.95, 5: 1.0, 6: 1.0,
          7: 1.0, 8: 1.0, 9: 1.1, 10: 1.1, 11: 1.5, 12: 1.4}


def generate(n_orders: int = 12_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    days = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    weights = np.linspace(1.0, 1.6, len(days)) * days.month.map(SEASON).to_numpy()
    weights = weights / weights.sum()

    cats = rng.choice(list(CATEGORIES), size=n_orders, p=[v[0] for v in CATEGORIES.values()])
    median = np.array([CATEGORIES[c][1] for c in cats])

    df = pd.DataFrame({
        "order_date": rng.choice(days.values, size=n_orders, p=weights),
        "customer_id": [f"KH{i:05d}" for i in rng.integers(1, 4000, n_orders)],
        "city": rng.choice(list(CITY_WEIGHTS), size=n_orders, p=list(CITY_WEIGHTS.values())),
        "category": cats,
        "quantity": rng.choice([1, 2, 3, 4, 5], size=n_orders, p=[0.62, 0.22, 0.10, 0.04, 0.02]),
        "unit_price": (median * rng.lognormal(0, 0.35, n_orders)).round(-3),
        "status": rng.choice(["Completed", "Cancelled"], size=n_orders, p=[0.92, 0.08]),
    }).sort_values("order_date").reset_index(drop=True)
    df.insert(0, "order_id", [f"DH{i:06d}" for i in range(1, n_orders + 1)])

    # ---- Thêm dữ liệu nhiễu ----
    # 1) tên thành phố viết sai định dạng (hoa/thường, thừa khoảng trắng)
    idx = rng.choice(n_orders, size=int(n_orders * 0.03), replace=False)
    for i in idx:
        s = df.at[i, "city"]
        df.at[i, "city"] = [s.lower(), s.upper(), f"  {s} "][rng.integers(0, 3)]
    # 2) thiếu giá / thiếu thành phố
    df.loc[rng.choice(n_orders, size=int(n_orders * 0.005), replace=False), "unit_price"] = np.nan
    df.loc[rng.choice(n_orders, size=int(n_orders * 0.004), replace=False), "city"] = np.nan
    # 3) dòng trùng lặp
    dup = df.sample(int(n_orders * 0.01), random_state=seed)
    df = pd.concat([df, dup]).sample(frac=1, random_state=seed).reset_index(drop=True)
    return df
