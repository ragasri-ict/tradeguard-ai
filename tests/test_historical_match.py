import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import pandas as pd

from backend.data.stock_data import StockData
from backend.data.market_data import MarketData
from backend.data.sector_data import SectorData
from backend.models.event_detector import EventDetector
from backend.models.historical_match import match_historical_events


# ==========================================
# 1. LOAD DATA
# ==========================================

stock = StockData()
market = MarketData()
sector = SectorData()
detector = EventDetector()


# ==========================================
# 2. SELECT STOCK
# ==========================================

symbol = "TCS"
sector_name = "NIFTY IT"
target_date = "2025-01-17"


# ==========================================
# 3. PREPARE STOCK DATA
# ==========================================

stock_data = stock.get_stock(symbol)

stock_data["Date"] = pd.to_datetime(
    stock_data["Date"],
    errors="coerce"
)

stock_data = stock_data.sort_values(
    "Date"
).reset_index(drop=True)


stock_data["Close Price"] = pd.to_numeric(
    stock_data["Close Price"],
    errors="coerce"
)

stock_data["Total Traded Quantity"] = pd.to_numeric(
    stock_data["Total Traded Quantity"],
    errors="coerce"
)


# ==========================================
# 4. STOCK RETURN
# ==========================================

stock_data["stock_return"] = (
    stock_data["Close Price"]
    .pct_change()
    * 100
)


# ==========================================
# 5. VOLUME RATIO
#
# Compare today's volume with the
# previous 5 trading days.
# ==========================================

previous_volume_average = (
    stock_data["Total Traded Quantity"]
    .shift(1)
    .rolling(window=5)
    .mean()
)

stock_data["volume_ratio"] = (
    stock_data["Total Traded Quantity"]
    / previous_volume_average
)


# ==========================================
# 6. GET VOLUME Z-SCORE
# ==========================================

detector_data = stock.get_detector_data(
    symbol
)

detector_result = detector.detect(
    detector_data
)

detector_result["Date"] = pd.to_datetime(
    detector_result["Date"],
    errors="coerce"
)

volume_features = detector_result[
    [
        "Date",
        "volume_zscore"
    ]
].copy()


# ==========================================
# 7. MERGE VOLUME FEATURES
# ==========================================

stock_data = stock_data.merge(
    volume_features,
    on="Date",
    how="left"
)


# ==========================================
# 8. PREPARE NIFTY 50 DATA
# ==========================================

market_data = market.get_data().copy()

market_data["Date"] = pd.to_datetime(
    market_data["Date"],
    errors="coerce"
)

market_data["Close"] = pd.to_numeric(
    market_data["Close"],
    errors="coerce"
)

market_data = market_data.sort_values(
    "Date"
).reset_index(drop=True)


market_data["nifty_return"] = (
    market_data["Close"]
    .pct_change()
    * 100
)


market_features = market_data[
    [
        "Date",
        "nifty_return"
    ]
].copy()


# ==========================================
# 9. PREPARE SECTOR DATA
# ==========================================

sector_data = sector.get_sector(
    sector_name
).copy()

sector_data["Date"] = pd.to_datetime(
    sector_data["Date"],
    errors="coerce"
)

sector_data["sector_return"] = pd.to_numeric(
    sector_data["sector_return"],
    errors="coerce"
)


sector_features = sector_data[
    [
        "Date",
        "sector_return"
    ]
].copy()


# ==========================================
# 10. MERGE MARKET + SECTOR
# ==========================================

events = stock_data.merge(
    market_features,
    on="Date",
    how="left"
)

events = events.merge(
    sector_features,
    on="Date",
    how="left"
)


# ==========================================
# 11. MARKET DIVERGENCE
# ==========================================

events["market_divergence"] = (
    events["stock_return"]
    - events["nifty_return"]
)


# ==========================================
# 12. KEEP REQUIRED COLUMNS
# ==========================================

events = events[
    [
        "Date",
        "Symbol",
        "stock_return",
        "volume_ratio",
        "volume_zscore",
        "nifty_return",
        "sector_return",
        "market_divergence"
    ]
].copy()


# ==========================================
# 13. REMOVE INCOMPLETE ROWS
# ==========================================

events = events.dropna(
    subset=[
        "Date",
        "stock_return",
        "volume_ratio",
        "volume_zscore",
        "nifty_return",
        "sector_return",
        "market_divergence"
    ]
).reset_index(drop=True)


# ==========================================
# 14. HISTORICAL MATCHING
# ==========================================

matched = match_historical_events(
    events,
    max_history=100,
    top_matches=5,
    minimum_history=20
)


# ==========================================
# 15. GET TARGET DATE
# ==========================================

target = matched[
    matched["Date"] ==
    pd.to_datetime(target_date)
]


# ==========================================
# 16. DISPLAY
# ==========================================

print("\nHISTORICAL EVENT MATCHING")
print("======================================")

print("Stock:", symbol)
print("Sector:", sector_name)
print("Target date:", target_date)

print("\nPrepared historical rows:")
print(len(events))

print(
    "\nHistorical date range:"
)
print(
    events["Date"].min(),
    "to",
    events["Date"].max()
)


if target.empty:

    print(
        "\nTarget date was not found."
    )

else:

    row = target.iloc[0]

    print("\n--- Current Fingerprint ---")

    print(
        "Stock return:",
        round(
            float(row["stock_return"]),
            4
        ),
        "%"
    )

    print(
        "Volume ratio:",
        round(
            float(row["volume_ratio"]),
            4
        )
    )

    print(
        "Volume z-score:",
        round(
            float(row["volume_zscore"]),
            4
        )
    )

    print(
        "NIFTY return:",
        round(
            float(row["nifty_return"]),
            4
        ),
        "%"
    )

    print(
        "Sector return:",
        round(
            float(row["sector_return"]),
            4
        ),
        "%"
    )

    print(
        "Market divergence:",
        round(
            float(row["market_divergence"]),
            4
        ),
        "%"
    )

    print("\n--- Historical Matching ---")

    print(
        "Historical match score:",
        row["historical_match_score"]
    )

    print(
        "Historical match count:",
        row["historical_match_count"]
    )

    print(
        "Historical average return:",
        row["historical_avg_return"],
        "%"
    )

    print(
        "Historical median return:",
        row["historical_median_return"],
        "%"
    )

    print(
        "Expected historical reaction:",
        row["expected_reaction"]
    )

    print(
        "\nHistorical match dates:"
    )

    print(
        row["historical_match_dates"]
    )

    print(
        "\nHistorical match returns:"
    )

    print(
        row["historical_match_returns"]
    )