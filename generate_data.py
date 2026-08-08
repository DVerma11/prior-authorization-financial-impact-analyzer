import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

N = 8000

PROCEDURES = {
    "70553": {
        "description": "MRI Brain w/wo Contrast",
        "base_cost": 950,
        "denial_rate": 0.14,
        "avoidance_probability": 0.78,
        "admin_cost_mean": 48,
        "monthly_trend": 0.004,
        "specialty": "Radiology",
    },
    "72148": {
        "description": "MRI Lumbar Spine",
        "base_cost": 700,
        "denial_rate": 0.22,
        "avoidance_probability": 0.72,
        "admin_cost_mean": 46,
        "monthly_trend": 0.006,
        "specialty": "Radiology",
    },
    "73721": {
        "description": "MRI Lower Extremity",
        "base_cost": 650,
        "denial_rate": 0.18,
        "avoidance_probability": 0.70,
        "admin_cost_mean": 44,
        "monthly_trend": 0.003,
        "specialty": "Radiology",
    },
    "27447": {
        "description": "Total Knee Arthroplasty",
        "base_cost": 18000,
        "denial_rate": 0.08,
        "avoidance_probability": 0.45,
        "admin_cost_mean": 72,
        "monthly_trend": 0.002,
        "specialty": "Orthopedics",
    },
    "29881": {
        "description": "Knee Arthroscopy",
        "base_cost": 4500,
        "denial_rate": 0.20,
        "avoidance_probability": 0.58,
        "admin_cost_mean": 60,
        "monthly_trend": -0.002,
        "specialty": "Orthopedics",
    },
    "64483": {
        "description": "Epidural Injection",
        "base_cost": 1200,
        "denial_rate": 0.25,
        "avoidance_probability": 0.62,
        "admin_cost_mean": 50,
        "monthly_trend": 0.005,
        "specialty": "Pain Management",
    },
    "93306": {
        "description": "Echocardiography",
        "base_cost": 500,
        "denial_rate": 0.07,
        "avoidance_probability": 0.40,
        "admin_cost_mean": 38,
        "monthly_trend": 0.001,
        "specialty": "Cardiology",
    },
    "43239": {
        "description": "Upper GI Endoscopy",
        "base_cost": 1500,
        "denial_rate": 0.12,
        "avoidance_probability": 0.52,
        "admin_cost_mean": 52,
        "monthly_trend": 0.003,
        "specialty": "Gastroenterology",
    },
}

codes = list(PROCEDURES.keys())

months = pd.period_range(
    "2024-01",
    "2025-12",
    freq="M",
)

rows = []

for i in range(N):
    code = np.random.choice(codes)
    p = PROCEDURES[code]

    month_index = np.random.randint(0, len(months))
    month = months[month_index]

    days_in_month = month.days_in_month
    day = np.random.randint(1, days_in_month + 1)

    service_date = pd.Timestamp(
        year=month.year,
        month=month.month,
        day=day,
    )

    # Small procedure-specific utilization trend.
    trend_multiplier = (
        1 + p["monthly_trend"] * month_index
    )

    allowed_amount = np.random.normal(
        p["base_cost"] * trend_multiplier,
        p["base_cost"] * 0.12,
    )

    allowed_amount = max(50, allowed_amount)

    denied = (
        np.random.random() < p["denial_rate"]
    )

    decision = "Denied" if denied else "Approved"

    admin_cost = np.random.normal(
        p["admin_cost_mean"],
        p["admin_cost_mean"] * 0.15,
    )

    admin_cost = max(15, admin_cost)

    # Important assumption:
    # A denied authorization does not automatically mean
    # the entire allowed amount was avoided.
    avoided_utilization = False
    realized_avoided_cost = 0.0

    if denied:
        avoided_utilization = (
            np.random.random()
            < p["avoidance_probability"]
        )

        if avoided_utilization:
            # Conservative fraction of expected allowed cost.
            realized_fraction = np.random.uniform(
                0.65,
                0.90,
            )

            realized_avoided_cost = (
                allowed_amount * realized_fraction
            )

    rows.append(
        {
            "claim_id": f"PA{i + 1:06d}",
            "member_id": (
                f"M{np.random.randint(1, 2500):05d}"
            ),
            "service_date": service_date,
            "procedure_code": code,
            "procedure_description": p["description"],
            "specialty": p["specialty"],
            "pa_decision": decision,
            "expected_allowed_cost": round(
                allowed_amount,
                2,
            ),
            "admin_cost": round(
                admin_cost,
                2,
            ),
            "avoided_utilization": (
                int(avoided_utilization)
            ),
            "estimated_avoided_cost": round(
                realized_avoided_cost,
                2,
            ),
        }
    )

df = pd.DataFrame(rows)

Path("data").mkdir(exist_ok=True)

df.to_csv(
    "data/synthetic_pa_claims.csv",
    index=False,
)

print(
    f"Created {len(df):,} synthetic PA records."
)