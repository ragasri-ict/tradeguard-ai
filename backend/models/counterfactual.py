import pandas as pd

from backend.models.attribution import calculate_attribution


def run_counterfactual(row, remove_factor):
    """
    Recalculate attribution after removing one
    evidence factor.

    This is an evidence-sensitivity analysis,
    not a causal probability calculation.
    """

    original_row = row.copy()

    # ---------------------------------------
    # Original attribution
    # ---------------------------------------

    original_attribution = calculate_attribution(
        original_row
    )

    # ---------------------------------------
    # Remove selected evidence
    # ---------------------------------------

    counterfactual_row = original_row.copy()

    if remove_factor == "company_event":

        counterfactual_row[
            "company_event_present"
        ] = False

    elif remove_factor == "sector_movement":

        counterfactual_row[
            "sector_return"
        ] = 0.0

    elif remove_factor == "market_movement":

        counterfactual_row[
            "nifty_return"
        ] = 0.0

        counterfactual_row[
            "market_divergence"
        ] = abs(
            float(
                counterfactual_row.get(
                    "stock_return",
                    0
                )
            )
        )

    elif remove_factor == "technical_flow":

        counterfactual_row[
            "volume_ratio"
        ] = 1.0

        counterfactual_row[
            "volume_zscore"
        ] = 0.0

    elif remove_factor == "stock_specific_move":

        counterfactual_row[
            "market_divergence"
        ] = 0.0

    else:

        raise ValueError(
            "Unknown counterfactual factor: "
            + str(remove_factor)
        )

    # ---------------------------------------
    # Counterfactual attribution
    # ---------------------------------------

    counterfactual_attribution = (
        calculate_attribution(
            counterfactual_row
        )
    )

    # ---------------------------------------
    # Compare primary cause
    # ---------------------------------------

    original_primary = (
        original_attribution[
            "primary_cause"
        ]
    )

    counterfactual_primary = (
        counterfactual_attribution[
            "primary_cause"
        ]
    )

    primary_cause_changed = (
        original_primary
        != counterfactual_primary
    )

    # ---------------------------------------
    # Compare attribution score
    # ---------------------------------------

    original_score = float(
        original_attribution[
            "attribution_confidence"
        ]
    )

    counterfactual_score = float(
        counterfactual_attribution[
            "attribution_confidence"
        ]
    )

    score_change = (
        original_score
        - counterfactual_score
    )

    # ---------------------------------------
    # Return result
    # ---------------------------------------

    return {

        "removed_factor":
            remove_factor,

        "original_primary_cause":
            original_primary,

        "counterfactual_primary_cause":
            counterfactual_primary,

        "original_score":
            round(
                original_score,
                2
            ),

        "counterfactual_score":
            round(
                counterfactual_score,
                2
            ),

        "score_change":
            round(
                score_change,
                2
            ),

        "primary_cause_changed":
            primary_cause_changed,

        "original_attribution":
            original_attribution,

        "counterfactual_attribution":
            counterfactual_attribution
    }


def run_all_counterfactuals(row):
    """
    Run counterfactual analysis for all
    supported evidence factors.
    """

    factors = [
        "company_event",
        "sector_movement",
        "market_movement",
        "technical_flow",
        "stock_specific_move"
    ]

    results = []

    for factor in factors:

        result = run_counterfactual(
            row,
            factor
        )

        results.append(result)

    return results