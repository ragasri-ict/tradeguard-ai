import pandas as pd


def generate_explanation(row, attribution):
    """
    Generate a human-readable explanation
    using stock, market, sector, technical,
    and company-event evidence.
    """

    # ---------------------------------------
    # Read values safely
    # ---------------------------------------

    stock_return = row.get("stock_return", 0)

    if pd.isna(stock_return):
        stock_return = 0

    stock_return = float(stock_return)

    sector_return = row.get("sector_return", 0)

    if pd.isna(sector_return):
        sector_return = 0

    sector_return = float(sector_return)

    nifty_return = row.get("nifty_return", 0)

    if pd.isna(nifty_return):
        nifty_return = 0

    nifty_return = float(nifty_return)

    volume_ratio = row.get("volume_ratio", 1)

    if pd.isna(volume_ratio):
        volume_ratio = 1

    volume_ratio = float(volume_ratio)

    company_event_present = row.get(
        "company_event_present",
        False
    )

    primary_cause = attribution.get(
        "primary_cause",
        "unknown"
    )

    confidence = attribution.get(
        "attribution_confidence",
        0
    )

    # ---------------------------------------
    # Stock movement description
    # ---------------------------------------

    if stock_return > 0:
        stock_direction = "increased"
    elif stock_return < 0:
        stock_direction = "decreased"
    else:
        stock_direction = "was unchanged"

    # ---------------------------------------
    # Sector description
    # ---------------------------------------

    if sector_return > 0:
        sector_direction = "increased"
    elif sector_return < 0:
        sector_direction = "decreased"
    else:
        sector_direction = "was unchanged"

    # ---------------------------------------
    # Market description
    # ---------------------------------------

    if nifty_return > 0:
        market_direction = "increased"
    elif nifty_return < 0:
        market_direction = "decreased"
    else:
        market_direction = "was unchanged"

    # ---------------------------------------
    # Volume description
    # ---------------------------------------

    if volume_ratio >= 2:
        volume_description = (
            f"Trading volume was approximately "
            f"{volume_ratio:.2f} times the recent average."
        )

    elif volume_ratio > 1:
        volume_description = (
            f"Trading volume was approximately "
            f"{volume_ratio:.2f} times the recent average."
        )

    else:
        volume_description = (
            f"Trading volume was approximately "
            f"{volume_ratio:.2f} times the recent average."
        )

    # ---------------------------------------
    # Company event description
    # ---------------------------------------

    if company_event_present:

        event_description = (
            "A company-specific event was found "
            "for this date."
        )

    else:

        event_description = (
            "No company-specific event was found "
            "for this date."
        )

    # ---------------------------------------
    # Primary cause explanation
    # ---------------------------------------

    cause_explanations = {

        "company_event":
            "The company-event factor received the "
            "highest rule-based attribution score.",

        "sector_movement":
            "The sector-movement factor received the "
            "highest rule-based attribution score.",

        "market_movement":
            "The broader market-movement factor received "
            "the highest rule-based attribution score.",

        "technical_flow":
            "Technical and trading-flow evidence received "
            "the highest rule-based attribution score.",

        "stock_specific_move":
            "The stock-specific movement factor received "
            "the highest rule-based attribution score.",

        "unknown":
            "The available evidence was not strong enough "
            "to assign a specific primary cause."
    }

    primary_explanation = cause_explanations.get(
        primary_cause,
        cause_explanations["unknown"]
    )

    # ---------------------------------------
    # Build explanation
    # ---------------------------------------

    explanation = (

        f"The stock {stock_direction} by "
        f"{abs(stock_return):.2f}% on the selected date. "

        f"The associated sector {sector_direction} by "
        f"{abs(sector_return):.2f}%, while the NIFTY 50 "
        f"{market_direction} by "
        f"{abs(nifty_return):.2f}%. "

        f"{volume_description} "

        f"{event_description} "

        f"{primary_explanation} "

        f"The rule-based attribution score for this "
        f"factor was {confidence:.2f}%."
    )

    return explanation