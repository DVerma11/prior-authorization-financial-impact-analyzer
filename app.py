import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import (
    monthly_summary,
    prepare_data,
    procedure_summary,
)
from src.projections import project_next_12_months


st.set_page_config(
    page_title=(
        "Prior Authorization Financial Impact Analyzer"
    ),
    layout="wide",
)

st.title(
    "Prior Authorization Financial Impact Analyzer"
)

st.caption(
    "Synthetic procedure-level utilization management "
    "analysis of prior authorization costs, estimated "
    "avoided utilization, net savings, and future trends."
)


df = pd.read_csv(
    "data/synthetic_pa_claims.csv",
    dtype={"procedure_code": str},
)

df = prepare_data(df)

procedure_df = procedure_summary(df)
monthly_df = monthly_summary(df)

projection_df = project_next_12_months(
    monthly_df
)


gross_avoided_cost = (
    df["estimated_avoided_cost"].sum()
)

admin_cost = df["admin_cost"].sum()

net_savings = (
    gross_avoided_cost - admin_cost
)

roi = (
    gross_avoided_cost / admin_cost
    if admin_cost > 0
    else 0
)

denial_rate = df["denied"].mean()


c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "PA Requests",
    f"{len(df):,}",
)

c2.metric(
    "Estimated Avoided Cost",
    f"${gross_avoided_cost:,.0f}",
)

c3.metric(
    "Administrative Cost",
    f"${admin_cost:,.0f}",
)

c4.metric(
    "Estimated Net Savings",
    f"${net_savings:,.0f}",
)

c5.metric(
    "Estimated ROI",
    f"{roi:.1f}x",
)


st.caption(
    "Financial estimates are based on synthetic assumptions "
    "and should not be interpreted as actual payer savings."
)

st.divider()


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Executive Overview",
        "Procedure Analysis",
        "Trends & Projections",
        "Strategic Review",
    ]
)


with tab1:

    st.subheader("Executive Overview")

    st.write(
        f"Overall PA denial rate: "
        f"**{denial_rate:.1%}**"
    )

    top_codes = procedure_df.head(5).copy()

    top_codes["procedure_label"] = (
        top_codes["procedure_code"]
        + " — "
        + top_codes["procedure_description"]
    )

    fig = px.bar(
        top_codes,
        x="procedure_label",
        y="net_savings",
        title=(
            "Top Procedures by Estimated Net Savings"
        ),
        labels={
            "procedure_label": "Procedure",
            "net_savings": "Estimated Net Savings ($)",
        },
    )

    fig.update_xaxes(
        type="category",
        tickangle=-30,
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )
    st.caption(
        "Higher estimated savings reflect the combined effect of "
        "procedure cost, denial rate, and the assumed probability "
        "that a denied service is not subsequently performed."
    )


with tab2:

    st.subheader(
        "Procedure-Level Financial Impact"
    )

    display_df = procedure_df.copy()

    display_df["denial_rate"] = (
        display_df["denial_rate"] * 100
    ).round(1)

    display_df[
        "avoidance_rate_among_denials"
    ] = (
        display_df[
            "avoidance_rate_among_denials"
        ]
        * 100
    ).round(1)

    currency_columns = [
        "avg_expected_cost",
        "gross_avoided_cost",
        "administrative_cost",
        "net_savings",
        "net_savings_per_pa",
    ]

    for column in currency_columns:
        display_df[column] = (
            display_df[column].round(2)
        )

    display_df["roi"] = (
        display_df["roi"].round(2)
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "procedure_code": st.column_config.TextColumn(
                "Procedure Code"
            ),
            "procedure_description": st.column_config.TextColumn(
                "Procedure",
                width="large",
            ),
            "specialty": st.column_config.TextColumn(
                "Specialty"
            ),
            "pa_volume": st.column_config.NumberColumn(
                "PA Volume",
                format="%d",
            ),
            "denied_requests": st.column_config.NumberColumn(
                "Denied",
                format="%d",
            ),
            "avoided_services": st.column_config.NumberColumn(
                "Est. Avoided Services",
                format="%d",
            ),
            "avg_expected_cost": st.column_config.NumberColumn(
                "Avg. Expected Cost",
                format="$%.0f",
            ),
            "gross_avoided_cost": st.column_config.NumberColumn(
                "Est. Avoided Cost",
                format="$%.0f",
            ),
            "administrative_cost": st.column_config.NumberColumn(
                "Admin Cost",
                format="$%.0f",
            ),
            "denial_rate": st.column_config.NumberColumn(
                "Denial Rate",
                format="%.1f%%",
            ),
            "avoidance_rate_among_denials": st.column_config.NumberColumn(
                "Avoidance Rate",
                format="%.1f%%",
            ),
            "net_savings": st.column_config.NumberColumn(
                "Net Savings",
                format="$%.0f",
            ),
            "roi": st.column_config.NumberColumn(
                "ROI",
                format="%.1fx",
            ),
            "net_savings_per_pa": st.column_config.NumberColumn(
                "Net Savings / PA",
                format="$%.0f",
            ),
        },
    )


    st.download_button(
        "Download Procedure Analysis",
        data=display_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name=(
            "procedure_level_analysis.csv"
        ),
        mime="text/csv",
    )


with tab3:

    st.subheader("Historical Trend")

    fig = px.line(
        monthly_df,
        x="month",
        y="net_savings",
        markers=True,
        title=(
            "Monthly Estimated Net Savings"
        ),
        labels={
            "month": "Month",
            "net_savings": (
                "Estimated Net Savings"
            ),
        },
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.subheader("12-Month Projection")

    st.caption(
        "Illustrative projection based on the historical monthly trend "
        "in the synthetic dataset; not a forecast of actual payer savings."
    )

    fig2 = px.line(
        projection_df,
        x="month",
        y="projected_net_savings",
        markers=True,
        title=(
            "Projected Monthly Net Savings"
        ),
        labels={
            "month": "Month",
            "projected_net_savings": (
                "Projected Net Savings"
            ),
        },
    )

    st.plotly_chart(
        fig2,
        width="stretch",
    )


with tab4:

    st.subheader("Strategic Review")

    st.write(
        "This section identifies procedures that may "
        "warrant further review based on the synthetic "
        "financial model."
    )

    high_value = procedure_df[
        (
            procedure_df["net_savings_per_pa"]
            > 300
        )
        & (procedure_df["roi"] >= 2)
    ]

    low_value = procedure_df[
        (
            procedure_df["roi"] < 1.5
        )
        | (
            procedure_df["net_savings_per_pa"]
            < 25
        )
    ]

    st.markdown(
        "### High-Value PA Procedures"
    )

    if high_value.empty:
        st.info(
            "No procedures met the current "
            "high-value criteria."
        )

    else:
        high_value_display = high_value[
            [
                "procedure_code",
                "procedure_description",
                "pa_volume",
                "denial_rate",
                "net_savings",
                "roi",
                "net_savings_per_pa",
            ]
        ].copy()

        high_value_display["denial_rate"] = (
            high_value_display["denial_rate"] * 100
        )

        st.dataframe(
            high_value_display,
            width="stretch",
            hide_index=True,
            column_config={
                "procedure_code": st.column_config.TextColumn(
                    "Procedure Code"
                ),
                "procedure_description": st.column_config.TextColumn(
                    "Procedure",
                    width="large",
                ),
                "pa_volume": st.column_config.NumberColumn(
                    "PA Volume",
                    format="%d",
                ),
                "denial_rate": st.column_config.NumberColumn(
                    "Denial Rate",
                    format="%.1f%%",
                ),
                "net_savings": st.column_config.NumberColumn(
                    "Net Savings",
                    format="$%.0f",
                ),
                "roi": st.column_config.NumberColumn(
                    "ROI",
                    format="%.1fx",
                ),
                "net_savings_per_pa": st.column_config.NumberColumn(
                    "Net Savings / PA",
                    format="$%.0f",
                ),
            },
        )



    st.markdown(
        "### Candidates for PA Policy Review"
    )

    st.caption(
        "Low estimated return does not mean prior "
        "authorization should automatically be removed. "
        "Clinical value, patient safety, fraud/waste risk, "
        "and policy requirements would also need review."
    )

    if low_value.empty:
        st.success(
            "No procedures met the current "
            "low-value review criteria."
        )
    else:
        low_value_display = low_value[
            [
                "procedure_code",
                "procedure_description",
                "pa_volume",
                "denial_rate",
                "administrative_cost",
                "net_savings",
                "roi",
            ]
        ].copy()

        low_value_display["denial_rate"] = (
            low_value_display["denial_rate"] * 100
        )

        st.dataframe(
            low_value_display,
            width="stretch",
            hide_index=True,
            column_config={
                "procedure_code": st.column_config.TextColumn(
                    "Procedure Code"
                ),
                "procedure_description": st.column_config.TextColumn(
                    "Procedure",
                    width="large",
                ),
                "pa_volume": st.column_config.NumberColumn(
                    "PA Volume",
                    format="%d",
                ),
                "denial_rate": st.column_config.NumberColumn(
                    "Denial Rate",
                    format="%.1f%%",
                ),
                "administrative_cost": st.column_config.NumberColumn(
                    "Admin Cost",
                    format="$%.0f",
                ),
                "net_savings": st.column_config.NumberColumn(
                    "Net Savings",
                    format="$%.0f",
                ),
                "roi": st.column_config.NumberColumn(
                    "ROI",
                    format="%.1fx",
                ),
            },
        )



st.divider()

with st.expander(
    "Model assumptions and limitations"
):
    st.markdown(
        """
**Synthetic data:** All records are artificially
generated and contain no real patient information.

**Estimated avoided utilization:** A denial does not
automatically count as full savings. Each procedure
has an assumed probability that a denied service is
not subsequently performed.

**Estimated avoided cost:** For simulated avoided
services, only a fraction of the expected allowed
amount is counted as avoided cost.

**Administrative cost:** Each PA request is assigned
an estimated processing cost.

**Net savings:** Estimated avoided cost minus PA
administrative cost.

**ROI:** Estimated avoided cost divided by
administrative cost.

These assumptions are illustrative and are intended
to demonstrate healthcare financial and operational
analytics rather than estimate actual payer savings.
"""
    )