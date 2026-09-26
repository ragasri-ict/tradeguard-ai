import os

from backend.data.market_data import (
    load_stock_data,
    load_nifty_data,
    prepare_stock_data,
    prepare_nifty_data
)

from backend.models.event_detector import detect_events

from backend.models.event_fingerprint import (
    create_event_fingerprint,
    extract_events
)


def main():

    print("\n================================")
    print("AI MARKET EVENT ATTRIBUTION")
    print("DATA PIPELINE")
    print("================================\n")

    # STEP 1
    print("STEP 1: Loading stock data...")
    stock = load_stock_data()

    # STEP 2
    print("\nSTEP 2: Preparing stock data...")
    stock = prepare_stock_data(stock)

    # STEP 3
    print("\nSTEP 3: Loading NIFTY data...")
    nifty = load_nifty_data()

    # STEP 4
    print("\nSTEP 4: Preparing NIFTY data...")
    nifty = prepare_nifty_data(nifty)

    # STEP 5
    print("\nSTEP 5: Detecting unusual events...")
    stock_events = detect_events(stock)

    # STEP 6
    print("\nSTEP 6: Creating event fingerprints...")
    fingerprints = create_event_fingerprint(
        stock_events,
        nifty
    )

    # STEP 7
    print("\nSTEP 7: Extracting detected events...")
    events = extract_events(fingerprints)

    # Create processed folder
    os.makedirs("data/processed", exist_ok=True)

    # Save market data
    fingerprints.to_csv(
        "data/processed/market_data.csv",
        index=False
    )

    # Save events
    events.to_csv(
        "data/processed/events.csv",
        index=False
    )

    # Save fingerprints
    events.to_csv(
        "data/processed/event_fingerprints.csv",
        index=False
    )

    print("\n================================")
    print("PIPELINE COMPLETED")
    print("================================")

    print("\nTotal market rows:", len(fingerprints))
    print("Total detected events:", len(events))

    print("\nCreated files:")

    print("✓ data/processed/market_data.csv")
    print("✓ data/processed/events.csv")
    print("✓ data/processed/event_fingerprints.csv")


if __name__ == "__main__":
    main()