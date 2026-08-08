import numpy as np
import pandas as pd


def prepare_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    df["service_date"] = pd.to_datetime(
        df["service_date"]
    )

    df["procedure_code"] = (
        df["procedure_code"]
        .astype(str)
        .str.strip()
    )

    df["month"] = (
        df["service_date"]
        .dt.to_period("M")
        .astype(str)
    )

    df["denied"] = (
        df["pa_decision"] == "Denied"
    ).astype(int)

    df["net_savings"] = (
        df["estimated_avoided_cost"]
        - df["admin_cost"]
    )

    return df


def procedure_summary(
    df: pd.DataFrame
) -> pd.DataFrame:

    summary = (
        df.groupby(
            [
                "procedure_code",
                "procedure_description",
                "specialty",
            ],
            as_index=False,
        )
        .agg(
            pa_volume=("claim_id", "count"),
            denied_requests=("denied", "sum"),
            avoided_services=(
                "avoided_utilization",
                "sum",
            ),
            avg_expected_cost=(
                "expected_allowed_cost",
                "mean",
            ),
            gross_avoided_cost=(
                "estimated_avoided_cost",
                "sum",
            ),
            administrative_cost=(
                "admin_cost",
                "sum",
            ),
        )
    )

    summary["denial_rate"] = (
        summary["denied_requests"]
        / summary["pa_volume"]
    )

    summary["avoidance_rate_among_denials"] = np.where(
        summary["denied_requests"] > 0,
        summary["avoided_services"]
        / summary["denied_requests"],
        0,
    )

    summary["net_savings"] = (
        summary["gross_avoided_cost"]
        - summary["administrative_cost"]
    )

    summary["roi"] = np.where(
        summary["administrative_cost"] > 0,
        summary["gross_avoided_cost"]
        / summary["administrative_cost"],
        np.nan,
    )

    summary["net_savings_per_pa"] = (
        summary["net_savings"]
        / summary["pa_volume"]
    )

    return summary.sort_values(
        "net_savings",
        ascending=False,
    )


def monthly_summary(
    df: pd.DataFrame
) -> pd.DataFrame:

    monthly = (
        df.groupby(
            "month",
            as_index=False,
        )
        .agg(
            pa_volume=("claim_id", "count"),
            denied_requests=("denied", "sum"),
            gross_avoided_cost=(
                "estimated_avoided_cost",
                "sum",
            ),
            administrative_cost=(
                "admin_cost",
                "sum",
            ),
        )
    )

    monthly["denial_rate"] = (
        monthly["denied_requests"]
        / monthly["pa_volume"]
    )

    monthly["net_savings"] = (
        monthly["gross_avoided_cost"]
        - monthly["administrative_cost"]
    )

    return monthly