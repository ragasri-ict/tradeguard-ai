import pandas as pd


def _safe_number(value, default=0.0):

    if value is None or pd.isna(value):
        return default

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _same_direction(first, second):

    if first == 0 or second == 0:
        return False

    return (
        (first > 0 and second > 0)
        or
        (first < 0 and second < 0)
    )


def calculate_attribution(row):

    scores = {
        "company_event": 0.0,
        "sector_movement": 0.0,
        "market_movement": 0.0,
        "technical_flow": 0.0,
        "stock_specific_move": 0.0,
        "unknown": 0.0
    }

    # ---------------------------------------
    # Read values safely
    # ---------------------------------------

    stock_return = _safe_number(
        row.get("stock_return", 0)
    )

    sector_return = _safe_number(
        row.get("sector_return", 0)
    )

    nifty_return = _safe_number(
        row.get("nifty_return", 0)
    )

    market_divergence = abs(
        _safe_number(
            row.get("market_divergence", 0)
        )
    )

    volume_ratio = _safe_number(
        row.get("volume_ratio", 1),
        1
    )

    # Prefer correctly named volume_zscore.
    # Keep return_zscore as a fallback so older
    # test files still work.
    volume_zscore = abs(
        _safe_number(
            row.get(
                "volume_zscore",
                row.get("return_zscore", 0)
            )
        )
    )

    company_event_present = bool(
        row.get(
            "company_event_present",
            False
        )
    )

    # ---------------------------------------
    # 1. COMPANY EVENT
    # ---------------------------------------

    if company_event_present:

        scores["company_event"] += 50


    # ---------------------------------------
    # 2. SECTOR MOVEMENT
    # ---------------------------------------

    sector_magnitude = abs(
        sector_return
    )

    if sector_magnitude >= 2:

        scores["sector_movement"] += 30

    elif sector_magnitude >= 1:

        scores["sector_movement"] += 20

    elif sector_magnitude >= 0.5:

        scores["sector_movement"] += 10


    # Stock and sector moving together provides
    # stronger sector evidence.

    if _same_direction(
        stock_return,
        sector_return
    ):

        scores["sector_movement"] += 15


    # ---------------------------------------
    # 3. MARKET MOVEMENT
    # ---------------------------------------

    market_magnitude = abs(
        nifty_return
    )

    if market_magnitude >= 2:

        scores["market_movement"] += 30

    elif market_magnitude >= 1:

        scores["market_movement"] += 20

    elif market_magnitude >= 0.5:

        scores["market_movement"] += 10


    # Stock and NIFTY moving together provides
    # stronger market evidence.

    if _same_direction(
        stock_return,
        nifty_return
    ):

        scores["market_movement"] += 15


    # ---------------------------------------
    # 4. TECHNICAL / TRADING FLOW
    # ---------------------------------------

    if volume_ratio >= 3:

        scores["technical_flow"] += 40

    elif volume_ratio >= 2:

        scores["technical_flow"] += 25

    elif volume_ratio >= 1.5:

        scores["technical_flow"] += 15


    if volume_zscore >= 3:

        scores["technical_flow"] += 20

    elif volume_zscore >= 2:

        scores["technical_flow"] += 15

    elif volume_zscore >= 1.5:

        scores["technical_flow"] += 10


    # ---------------------------------------
    # 5. STOCK-SPECIFIC MOVEMENT
    # ---------------------------------------

    if market_divergence >= 5:

        scores["stock_specific_move"] += 40

    elif market_divergence >= 3:

        scores["stock_specific_move"] += 30

    elif market_divergence >= 2:

        scores["stock_specific_move"] += 20

    elif market_divergence >= 1:

        scores["stock_specific_move"] += 10


    # ---------------------------------------
    # 6. UNKNOWN
    #
    # Only use unknown when there is no
    # meaningful evidence.
    # ---------------------------------------

    evidence_total = sum(
        scores[key]
        for key in scores
        if key != "unknown"
    )

    if evidence_total == 0:

        scores["unknown"] = 100


    # ---------------------------------------
    # NORMALIZE
    # ---------------------------------------

    total = sum(
        scores.values()
    )

    if total > 0:

        for key in scores:

            scores[key] = (
                scores[key] / total
            ) * 100


    # ---------------------------------------
    # PRIMARY CAUSE
    # ---------------------------------------

    primary_cause = max(
        scores,
        key=scores.get
    )

    attribution_score = scores[
        primary_cause
    ]


    # ---------------------------------------
    # RETURN
    # ---------------------------------------

    return {

        "company_event_score": round(
            scores["company_event"],
            2
        ),

        "sector_movement_score": round(
            scores["sector_movement"],
            2
        ),

        "market_movement_score": round(
            scores["market_movement"],
            2
        ),

        "technical_flow_score": round(
            scores["technical_flow"],
            2
        ),

        "stock_specific_move_score": round(
            scores["stock_specific_move"],
            2
        ),

        "unknown_score": round(
            scores["unknown"],
            2
        ),

        "primary_cause": primary_cause,

        "attribution_confidence": round(
            attribution_score,
            2
        )
    }


def generate_attributions(events):

    results = []

    for _, row in events.iterrows():

        attribution = calculate_attribution(
            row
        )

        result = row.to_dict()

        result.update(
            attribution
        )

        results.append(result)

    return pd.DataFrame(
        results
    )