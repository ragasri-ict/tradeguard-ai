import pandas as pd
import numpy as np


# Features used to compare the current event
# with previous historical events.
FEATURES = [
    "stock_return",
    "volume_ratio",
    "volume_zscore",
    "nifty_return",
    "sector_return",
    "market_divergence"
]


def prepare_features(df):
    """
    Prepare and normalize features used
    for historical event matching.
    """

    df = df.copy()

    for column in FEATURES:

        if column not in df.columns:
            df[column] = 0.0

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        df[column] = df[column].fillna(0)

    # Prevent extreme observations from
    # dominating similarity.
    df["stock_return"] = (
        df["stock_return"].clip(-20, 20)
    )

    df["volume_ratio"] = (
        df["volume_ratio"].clip(0, 10)
    )

    df["volume_zscore"] = (
        df["volume_zscore"].clip(-5, 5)
    )

    df["nifty_return"] = (
        df["nifty_return"].clip(-10, 10)
    )

    df["sector_return"] = (
        df["sector_return"].clip(-10, 10)
    )

    df["market_divergence"] = (
        df["market_divergence"].clip(-20, 20)
    )

    # Robust scaling using median and IQR.
    scaled = pd.DataFrame(
        index=df.index
    )

    for column in FEATURES:

        median = df[column].median()

        q1 = df[column].quantile(0.25)

        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        if iqr == 0 or pd.isna(iqr):
            iqr = 1

        scaled[column] = (
            (df[column] - median) / iqr
        )

    return scaled


def calculate_similarity(
    current_vector,
    previous_matrix
):
    """
    Calculate Euclidean distance and convert
    it into a similarity score.
    """

    differences = (
        previous_matrix - current_vector
    )

    distances = np.sqrt(
        np.mean(
            differences ** 2,
            axis=1
        )
    )

    similarities = (
        1 / (1 + distances)
    )

    return similarities, distances


def match_historical_events(
    events,
    max_history=50,
    top_matches=3,
    minimum_history=10
):
    """
    Compare each event with previous events
    of the same stock.

    Future events are never used.
    """

    df = events.copy()

    # ------------------------------------------------
    # Support both Symbol and SYMBOL
    # ------------------------------------------------

    if "Symbol" in df.columns:

        df["SYMBOL"] = (
            df["Symbol"]
            .astype(str)
            .str.strip()
        )

    elif "SYMBOL" in df.columns:

        df["SYMBOL"] = (
            df["SYMBOL"]
            .astype(str)
            .str.strip()
        )

    else:

        raise ValueError(
            "Historical matching requires "
            "'Symbol' or 'SYMBOL' column."
        )


    # ------------------------------------------------
    # Date
    # ------------------------------------------------

    if "Date" not in df.columns:

        raise ValueError(
            "Historical matching requires "
            "'Date' column."
        )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Date"]
    )


    # ------------------------------------------------
    # Sort
    # ------------------------------------------------

    df = df.sort_values(
        ["SYMBOL", "Date"]
    ).reset_index(
        drop=True
    )


    # ------------------------------------------------
    # Prepare features
    # ------------------------------------------------

    scaled_features = prepare_features(
        df
    )

    results = []


    # ------------------------------------------------
    # Process each stock separately
    # ------------------------------------------------

    for symbol, group in df.groupby(
        "SYMBOL"
    ):

        indexes = group.index.tolist()

        symbol_features = (
            scaled_features.loc[indexes]
            .values
        )

        symbol_returns = pd.to_numeric(
            group["stock_return"],
            errors="coerce"
        ).fillna(0).values

        symbol_dates = group[
            "Date"
        ].values


        # --------------------------------------------
        # Compare every current event with history
        # --------------------------------------------

        for position in range(
            len(indexes)
        ):

            # Current event is not included
            # in its own history.
            history_end = position

            history_start = max(
                0,
                history_end - max_history
            )

            history_count = (
                history_end - history_start
            )


            # ----------------------------------------
            # Not enough previous history
            # ----------------------------------------

            if history_count < minimum_history:

                results.append({

                    "historical_match_score":
                        0.0,

                    "historical_match_count":
                        0,

                    "historical_avg_return":
                        np.nan,

                    "historical_median_return":
                        np.nan,

                    "expected_reaction":
                        "INSUFFICIENT_HISTORY",

                    "historical_match_dates":
                        "",

                    "historical_match_returns":
                        ""
                })

                continue


            # ----------------------------------------
            # Historical feature matrix
            # ----------------------------------------

            previous_matrix = (
                symbol_features[
                    history_start:
                    history_end
                ]
            )

            current_vector = (
                symbol_features[position]
            )


            # ----------------------------------------
            # Similarity
            # ----------------------------------------

            similarities, distances = (
                calculate_similarity(
                    current_vector,
                    previous_matrix
                )
            )


            # ----------------------------------------
            # Best historical matches
            # ----------------------------------------

            order = np.argsort(
                similarities
            )[::-1]

            selected = order[
                :min(
                    top_matches,
                    len(order)
                )
            ]


            selected_similarities = (
                similarities[selected]
            )

            historical_returns = (
                symbol_returns[
                    history_start:
                    history_end
                ][selected]
            )

            historical_dates = (
                symbol_dates[
                    history_start:
                    history_end
                ][selected]
            )


            # ----------------------------------------
            # Match score
            # ----------------------------------------

            best_similarity = float(
                selected_similarities[0]
            )

            match_score = min(
                100,
                best_similarity * 100
            )


            # ----------------------------------------
            # Historical reaction
            # ----------------------------------------

            avg_return = float(
                np.mean(
                    historical_returns
                )
            )

            median_return = float(
                np.median(
                    historical_returns
                )
            )


            if median_return > 0:

                expected_reaction = (
                    "POSITIVE"
                )

            elif median_return < 0:

                expected_reaction = (
                    "NEGATIVE"
                )

            else:

                expected_reaction = (
                    "NEUTRAL"
                )


            # ----------------------------------------
            # Dates and returns
            # ----------------------------------------

            date_strings = [

                pd.Timestamp(
                    value
                ).strftime(
                    "%Y-%m-%d"
                )

                for value
                in historical_dates

            ]


            return_strings = [

                round(
                    float(value),
                    2
                )

                for value
                in historical_returns

            ]


            # ----------------------------------------
            # Save result
            # ----------------------------------------

            results.append({

                "historical_match_score":
                    round(
                        match_score,
                        2
                    ),

                "historical_match_count":
                    len(selected),

                "historical_avg_return":
                    round(
                        avg_return,
                        2
                    ),

                "historical_median_return":
                    round(
                        median_return,
                        2
                    ),

                "expected_reaction":
                    expected_reaction,

                "historical_match_dates":
                    "|".join(
                        date_strings
                    ),

                "historical_match_returns":
                    "|".join(
                        map(
                            str,
                            return_strings
                        )
                    )
            })


    # ------------------------------------------------
    # Combine results
    # ------------------------------------------------

    result_df = pd.DataFrame(
        results
    )

    final_df = pd.concat(
        [
            df.reset_index(
                drop=True
            ),

            result_df
        ],
        axis=1
    )

    return final_df