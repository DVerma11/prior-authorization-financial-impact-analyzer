import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def project_next_12_months(
    monthly_df: pd.DataFrame
) -> pd.DataFrame:

    df = monthly_df.copy()

    df["month_num"] = np.arange(len(df))

    model = LinearRegression()

    X = df[["month_num"]]
    y = df["net_savings"]

    model.fit(X, y)

    future_month_num = np.arange(
        len(df),
        len(df) + 12
    )

    predictions = model.predict(
        future_month_num.reshape(-1, 1)
    )

    last_month = pd.Period(
        df["month"].iloc[-1],
        freq="M"
    )

    future_months = [
        str(last_month + i)
        for i in range(1, 13)
    ]

    return pd.DataFrame({
        "month": future_months,
        "projected_net_savings": predictions
    })