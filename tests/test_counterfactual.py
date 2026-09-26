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
from backend.models.counterfactual import run_all_counterfactuals


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
# 3. GET STOCK DATA
# ==========================================

stock_data = stock.get_stock(symbol)

stock_data["Date"] = pd.to_datetime(
    stock_data["Date"],
    errors="coerce"
)

stock_data = stock_data.sort_values(
    "Date"
).reset_index(drop=True)


# ==========================================
# 4. STOCK RETURN
# ==========================================

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
# 5. VOLUME RATIO
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
# 6. VOLUME Z-SCORE
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
# 7. NIFTY 50
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
# 8. SECTOR
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
# 9. MERGE
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
# 10. MARKET DIVERGENCE
# ==========================================

data["market_divergence"] = (
    data["stock_return"]
    - data["nifty_return"]
)


# ==========================================
# 11. TARGET ROW
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
# 12. COMPANY EVENT
# ==========================================

company_events = events.get_events(
    symbol,
    date
)

company_event_present = (
    not company_events.empty
)


# ==========================================
# 13. CREATE ATTRIBUTION INPUT
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
# 14. ORIGINAL ATTRIBUTION
# ==========================================

original = calculate_attribution(
    attribution_row
)


# ==========================================
# 15. COUNTERFACTUAL ANALYSIS
# ==========================================

results = run_all_counterfactuals(
    attribution_row
)


# ==========================================
# 16. DISPLAY
# ==========================================

print("\nCOUNTERFACTUAL ANALYSIS")
print("======================================")

print("Date:", date)
print("Stock:", symbol)
print("Sector:", sector_name)

print("\n--- Original Attribution ---")

print(
    "Primary cause:",
    original["primary_cause"]
)

print(
    "Attribution score:",
    original["attribution_confidence"],
    "%"
)


print("\n--- Counterfactual Results ---")


for result in results:

    print("\nRemoving:",
          result["removed_factor"])

    print(
        "Original primary cause:",
        result["original_primary_cause"]
    )

    print(
        "Counterfactual primary cause:",
        result["counterfactual_primary_cause"]
    )

    print(
        "Original score:",
        result["original_score"],
        "%"
    )

    print(
        "Counterfactual score:",
        result["counterfactual_score"],
        "%"
    )

    print(
        "Score change:",
        result["score_change"],
        "percentage points"
    )

    print(
        "Primary cause changed:",
        result["primary_cause_changed"]
    )