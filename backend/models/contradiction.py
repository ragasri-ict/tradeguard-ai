import pandas as pd


def _safe_number(value, default=0.0):

    if value is None or pd.isna(value):
        return default

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def same_direction(first, second):

    if first == 0 or second == 0:
        return False

    return (
        (first > 0 and second > 0)
        or
        (first < 0 and second < 0)
    )


def analyze_alternative_causes(row, attribution):
    """
    Identify supporting and alternative evidence
    for the current attribution.

    This does not prove causality.
    It highlights evidence that supports or
    competes with the primary attribution.
    """

    stock_return = _safe_number(
        row.get("stock_return", 0)
    )

    sector_return = _safe_number(
        row.get("sector_return", 0)
    )

    nifty_return = _safe_number(
        row.get("nifty_return", 0)
    )

    volume_ratio = _safe_number(
        row.get("volume_ratio", 1),
        1
    )

    volume_zscore = _safe_number(
        row.get("volume_zscore", 0)
    )

    market_divergence = abs(
        _safe_number(
            row.get("market_divergence", 0)
        )
    )

    company_event_present = bool(
        row.get(
            "company_event_present",
            False
        )
    )

    primary_cause = attribution.get(
        "primary_cause",
        "unknown"
    )

    alternatives = []
    contradictions = []


    # ---------------------------------------
    # Company event evidence
    # ---------------------------------------

    if company_event_present:

        alternatives.append({
            "factor": "company_event",
            "type": "supporting_evidence",
            "message":
                "A company-specific event was found "
                "on the selected date."
        })


    # ---------------------------------------
    # Sector evidence
    # ---------------------------------------

    if abs(sector_return) >= 1:

        sector_message = (
            f"The sector moved by "
            f"{sector_return:.2f}%."
        )

        if same_direction(
            stock_return,
            sector_return
        ):

            sector_message += (
                " The stock and sector moved "
                "in the same direction, providing "
                "alternative sector-level evidence."
            )

            alternatives.append({
                "factor": "sector_movement",
                "type": "alternative_cause",
                "message": sector_message
            })

        else:

            contradictions.append({
                "factor": "sector_movement",
                "type": "direction_conflict",
                "message":
                    "The stock and sector moved "
                    "in opposite directions."
            })


    # ---------------------------------------
    # Market evidence
    # ---------------------------------------

    if abs(nifty_return) >= 1:

        if same_direction(
            stock_return,
            nifty_return
        ):

            alternatives.append({
                "factor": "market_movement",
                "type": "alternative_cause",
                "message":
                    "The stock and NIFTY 50 moved "
                    "in the same direction."
            })

        else:

            contradictions.append({
                "factor": "market_movement",
                "type": "direction_conflict",
                "message":
                    "The stock and NIFTY 50 moved "
                    "in opposite directions."
            })


    # ---------------------------------------
    # Technical evidence
    # ---------------------------------------

    if (
        volume_ratio >= 2
        or abs(volume_zscore) >= 2
    ):

        alternatives.append({
            "factor": "technical_flow",
            "type": "alternative_cause",
            "message":
                "Trading activity was unusually high "
                "relative to recent observations."
        })


    # ---------------------------------------
    # Stock-specific evidence
    # ---------------------------------------

    if market_divergence >= 2:

        alternatives.append({
            "factor": "stock_specific_move",
            "type": "alternative_cause",
            "message":
                "The stock showed a meaningful divergence "
                "from the broader market."
        })


    # ---------------------------------------
    # Primary cause versus alternatives
    # ---------------------------------------

    alternative_causes = [
        item
        for item in alternatives
        if item["factor"] != primary_cause
    ]


    # ---------------------------------------
    # Overall interpretation
    # ---------------------------------------

    if contradictions:

        interpretation = (
            "Some evidence sources disagree with "
            "each other. The attribution should "
            "therefore be treated as mixed evidence."
        )

    elif alternative_causes:

        interpretation = (
            "The primary attribution has one or "
            "more meaningful alternative explanations."
        )

    else:

        interpretation = (
            "No strong alternative explanation was "
            "identified from the available evidence."
        )


    return {
        "primary_cause": primary_cause,
        "alternative_causes": alternative_causes,
        "contradictory_evidence": contradictions,
        "interpretation": interpretation
    }