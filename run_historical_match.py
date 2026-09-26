import os
import pandas as pd

from backend.models.historical_match import (
    match_historical_events
)


INPUT_FILE = "data/processed/events.csv"
OUTPUT_FILE = "data/processed/historical_matches.csv"


def main():

    print("\n================================")
    print("HISTORICAL EVENT MATCHING")
    print("================================\n")

    print("Loading detected events...")

    events = pd.read_csv(
        INPUT_FILE
    )

    print(
        "Events loaded:",
        len(events)
    )

    print("\nFinding similar previous events...")

    matched_events = match_historical_events(
        events,
        max_history=50,
        top_matches=3,
        minimum_history=3
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    matched_events.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n================================")
    print("HISTORICAL MATCHING COMPLETED")
    print("================================")

    print(
        "\nTotal events:",
        len(matched_events)
    )

    matched_count = (
        matched_events[
            "historical_match_count"
        ] > 0
    ).sum()

    print(
        "Events with historical matches:",
        matched_count
    )

    print("\nExpected reaction distribution:")

    print(
        matched_events[
            "expected_reaction"
        ].value_counts()
    )

    print("\nSample results:")

    columns = [
        "SYMBOL",
        "Date",
        "stock_return",
        "historical_match_score",
        "historical_match_count",
        "historical_avg_return",
        "historical_median_return",
        "expected_reaction",
        "historical_match_dates"
    ]

    available_columns = [
        column
        for column in columns
        if column in matched_events.columns
    ]

    print(
        matched_events[
            available_columns
        ].head(10).to_string(
            index=False
        )
    )

    print("\nCreated:")
    print(
        "✓",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()