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
from backend.data.company_events import CompanyEvents
from backend.models.event_detector import EventDetector
from backend.models.attribution import calculate_attribution
from backend.models.contradiction import (
    analyze_alternative_causes
)


# ==========================================
# 1. LOAD DATA
# ==========================================

stock = StockData()
market = MarketData()
sector = SectorData()
events = CompanyEvents()
detector = EventDetector()


# ==========================================
# 2. SELECT STOCK AND DATE
# ==========================================

symbol = "TCS"
sector_name = "NIFTY IT"
date = "2025-01-17"

target_date = pd.to_datetime(date)


# ==========================================
# 3. STOCK DATA
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

stock_data["stock_return"] = (
    stock_data["Close Price"]
    .pct_change()
    * 100
)


# ==========================================
# 4. VOLUME RATIO
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
# 5. VOLUME Z-SCORE
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

stock_data = stock_data.merge(
    volume_features,
    on="Date",
    how="left"
)


# ==========================================
# 6. NIFTY 50
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
# 7. SECTOR
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
# 8. MERGE
# ==========================================

data = stock_data.merge(
    market_features,
    on="Date",
    how="left"
)

data = data.merge(
    sector_features,
    on="Date",
    how="left"
)


# ==========================================
# 9. MARKET DIVERGENCE
# ==========================================

data["market_divergence"] = (
    data["stock_return"]
    - data["nifty_return"]
)


# ==========================================
# 10. TARGET ROW
# ==========================================

target = data[
    data["Date"] == target_date
]

if target.empty:

    print(
        "Target date not found:",
        date
    )

    exit()


row = target.iloc[0]


# ==========================================
# 11. COMPANY EVENT
# ==========================================

company_events = events.get_events(
    symbol,
    date
)

company_event_present = (
    not company_events.empty
)


# ==========================================
# 12. ATTRIBUTION INPUT
# ==========================================

attribution_row = {

    "stock_return":
        float(row["stock_return"]),

    "sector_return":
        float(row["sector_return"]),

    "nifty_return":
        float(row["nifty_return"]),

    "market_divergence":
        float(row["market_divergence"]),

    "volume_ratio":
        float(row["volume_ratio"]),

    "volume_zscore":
        float(row["volume_zscore"]),

    "company_event_present":
        company_event_present
}


# ==========================================
# 13. ATTRIBUTION
# ==========================================

attribution = calculate_attribution(
    attribution_row
)


# ==========================================
# 14. ALTERNATIVE CAUSE ANALYSIS
# ==========================================

analysis = analyze_alternative_causes(
    attribution_row,
    attribution
)


# ==========================================
# 15. DISPLAY
# ==========================================

print("\nALTERNATIVE / CONTRADICTORY CAUSE ANALYSIS")
print("============================================")

print("Date:", date)
print("Stock:", symbol)
print("Sector:", sector_name)


print("\n--- Primary Attribution ---")

print(
    "Primary cause:",
    analysis["primary_cause"]
)

print(
    "Attribution score:",
    attribution["attribution_confidence"],
    "%"
)


print("\n--- Alternative Evidence ---")


if analysis["alternative_causes"]:

    for item in analysis[
        "alternative_causes"
    ]:

        print(
            "\nFactor:",
            item["factor"]
        )

        print(
            "Type:",
            item["type"]
        )

        print(
            "Explanation:",
            item["message"]
        )

else:

    print(
        "No strong alternative cause identified."
    )


print("\n--- Contradictory Evidence ---")


if analysis["contradictory_evidence"]:

    for item in analysis[
        "contradictory_evidence"
    ]:

        print(
            "\nFactor:",
            item["factor"]
        )

        print(
            "Type:",
            item["type"]
        )

        print(
            "Explanation:",
            item["message"]
        )

else:

    print(
        "No contradictory evidence identified."
    )


print("\n--- Overall Interpretation ---")

print(
    analysis["interpretation"]
)
