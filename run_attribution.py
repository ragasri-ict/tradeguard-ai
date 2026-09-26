import os
import pandas as pd

from backend.models.attribution import (
    generate_attributions
)


INPUT_FILE = (
    "data/processed/events.csv"
)

OUTPUT_FILE = (
    "data/processed/attributions.csv"
)


def main():

    print("\n================================")
    print("MARKET EVENT ATTRIBUTION")
    print("================================\n")

    # Load detected events
    print("Loading detected events...")

    events = pd.read_csv(
        INPUT_FILE
    )

    print(
        "Events loaded:",
        len(events)
    )

    # Generate attribution
    print(
        "\nCalculating candidate causes..."
    )

    attributions = generate_attributions(
        events
    )

    # Create processed folder
    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    # Save
    attributions.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\n================================"
    )

    print(
        "ATTRIBUTION COMPLETED"
    )

    print(
        "================================"
    )

    print(
        "\nTotal attributed events:",
        len(attributions)
    )

    print(
        "\nCreated:"
    )

    print(
        "✓",
        OUTPUT_FILE
    )

    print(
        "\nPrimary cause distribution:"
    )

    print(
        attributions[
            "primary_cause"
        ].value_counts()
    )

    print(
        "\nSample results:"
    )

    columns = [
        "SYMBOL",
        "Date",
        "stock_return",
        "nifty_return",
        "market_divergence",
        "primary_cause",
        "attribution_confidence"
    ]

    available_columns = [
        col
        for col in columns
        if col in attributions.columns
    ]

    print(
        attributions[
            available_columns
        ].head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()