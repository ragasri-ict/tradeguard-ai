import pandas as pd
import numpy as np


def create_event_fingerprint(stock_df, nifty_df):
    """
    Combine stock events with NIFTY market context.

    The function matches stock data and NIFTY data
    using the trading date.
    """

    stock_df = stock_df.copy()
    nifty_df = nifty_df.copy()

    # --------------------------------------------------
    # Prepare dates
    # --------------------------------------------------

    stock_df["Date"] = pd.to_datetime(
        stock_df["Date"],
        errors="coerce"
    )

    nifty_df["Date"] = pd.to_datetime(
        nifty_df["Date"],
        errors="coerce"
    )

    # --------------------------------------------------
    # Select required NIFTY columns
    # --------------------------------------------------

    nifty_small = nifty_df[
        ["Date", "nifty_return"]
    ].copy()

    # Remove duplicate NIFTY dates
    nifty_small = (
        nifty_small
        .drop_duplicates(subset=["Date"])
    )

    # --------------------------------------------------
    # Merge stock + NIFTY
    # --------------------------------------------------

    merged = pd.merge(
        stock_df,
        nifty_small,
        on="Date",
        how="left"
    )

    # --------------------------------------------------
    # Calculate market divergence
    # --------------------------------------------------

    merged["market_divergence"] = (
        merged["stock_return"]
        - merged["nifty_return"]
    )

    # --------------------------------------------------
    # Price shock
    # --------------------------------------------------

    merged["price_shock"] = (
        merged["stock_return"].abs()
    )

    # --------------------------------------------------
    # Market shock
    # --------------------------------------------------

    merged["market_shock"] = (
        merged["nifty_return"].abs()
    )

    # --------------------------------------------------
    # Relative stock movement
    # --------------------------------------------------

    merged["relative_market_move"] = (
        merged["stock_return"]
        - merged["nifty_return"]
    )

    # --------------------------------------------------
    # Fingerprint components
    # --------------------------------------------------

    merged["price_component"] = (
        merged["price_shock"]
        .fillna(0)
        .clip(upper=15)
    )

    merged["volume_component"] = (
        merged["volume_ratio"]
        .fillna(1)
        .clip(upper=10)
    )

    merged["market_component"] = (
        merged["market_divergence"]
        .abs()
        .fillna(0)
        .clip(upper=15)
    )

    merged["zscore_component"] = (
        merged["return_zscore"]
        .abs()
        .fillna(0)
        .clip(upper=5)
    )

    # --------------------------------------------------
    # Event fingerprint score
    # --------------------------------------------------

    merged["fingerprint_score"] = (
        merged["price_component"] * 0.30
        + merged["volume_component"] * 0.20
        + merged["market_component"] * 0.30
        + merged["zscore_component"] * 0.20
    )

    # --------------------------------------------------
    # Market context
    # --------------------------------------------------

    merged["market_context"] = "UNKNOWN"

    merged.loc[
        merged["nifty_return"] >= 1,
        "market_context"
    ] = "MARKET_UP"

    merged.loc[
        merged["nifty_return"] <= -1,
        "market_context"
    ] = "MARKET_DOWN"

    merged.loc[
        merged["nifty_return"].between(-1, 1),
        "market_context"
    ] = "MARKET_NEUTRAL"

    # --------------------------------------------------
    # Stock vs market behaviour
    # --------------------------------------------------

    merged["relative_strength"] = "NORMAL"

    merged.loc[
        merged["market_divergence"] >= 2,
        "relative_strength"
    ] = "STRONG_OUTPERFORMANCE"

    merged.loc[
        merged["market_divergence"] <= -2,
        "relative_strength"
    ] = "STRONG_UNDERPERFORMANCE"

    # --------------------------------------------------
    # Event fingerprint label
    # --------------------------------------------------

    def create_label(row):

        if not row["is_event"]:
            return "NORMAL"

        price = row["price_shock"]
        volume = row["volume_ratio"]
        divergence = abs(
            row["market_divergence"]
        )

        if price >= 5 and volume >= 3:
            return "PRICE_VOLUME_SHOCK"

        if divergence >= 3:
            return "MARKET_DIVERGENCE"

        if volume >= 3:
            return "VOLUME_SHOCK"

        if price >= 5:
            return "PRICE_SHOCK"

        return "MULTI_SIGNAL_EVENT"

    merged["event_fingerprint"] = (
        merged.apply(
            create_label,
            axis=1
        )
    )

    return merged


def extract_events(df):
    """
    Extract only detected market events.
    """

    events = df[
        df["is_event"] == True
    ].copy()

    # Sort strongest events first
    events = events.sort_values(
        "fingerprint_score",
        ascending=False
    )

    return events