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
from backend.models.explainability import generate_explanation


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
    stock_data["Date"]
)

stock_data = stock_data.sort_values(
    "Date"
).reset_index(drop=True)

detector_data = stock.get_detector_data(symbol)

detector_result = detector.detect(detector_data)


# ==========================================
# 4. GET TARGET ROW
# ==========================================

stock_row = stock_data[
    stock_data["Date"] == target_date
]

detector_row = detector_result[
    detector_result["Date"] == target_date
]


if stock_row.empty:
    print("Stock data not available for", date)
    exit()


if detector_row.empty:
    print("Detector data not available for", date)
    exit()


# ==========================================
# 5. STOCK RETURN
# ==========================================

previous_rows = stock_data[
    stock_data["Date"] < target_date
]

if previous_rows.empty:
    print("Previous stock data not available.")
    exit()


current_close = float(
    stock_row.iloc[0]["Close Price"]
)

previous_close = float(
    previous_rows.iloc[-1]["Close Price"]
)

stock_return = (
    (current_close - previous_close)
    / previous_close
) * 100


# ==========================================
# 6. VOLUME
# ==========================================

volume = float(
    detector_row.iloc[0]["Volume"]
)

volume_zscore = float(
    detector_row.iloc[0]["volume_zscore"]
)


previous_detector_rows = detector_result[
    detector_result["Date"] < target_date
]

previous_5 = previous_detector_rows.tail(5)


if len(previous_5) > 0:

    previous_volume_mean = (
        previous_5["Volume"].mean()
    )

    if previous_volume_mean > 0:

        volume_ratio = (
            volume / previous_volume_mean
        )

    else:

        volume_ratio = 1.0

else:

    volume_ratio = 1.0


# ==========================================
# 7. MARKET RETURN
# ==========================================

market_return = market.get_market_return(date)

if market_return is None:

    market_return_percent = 0.0

else:

    market_return_percent = (
        market_return * 100
    )


# ==========================================
# 8. SECTOR RETURN
# ==========================================

sector_return = sector.get_sector_return(
    sector_name,
    date
)

if sector_return is None:

    sector_return = 0.0


# ==========================================
# 9. MARKET DIVERGENCE
# ==========================================

market_divergence = (
    stock_return - market_return_percent
)


# ==========================================
# 10. COMPANY EVENT
# ==========================================

company_events = events.get_events(
    symbol,
    date
)

company_event_present = (
    not company_events.empty
)


# ==========================================
# 11. ATTRIBUTION INPUT
# ==========================================

attribution_row = {

    "stock_return": stock_return,

    "sector_return": sector_return,

    "nifty_return": market_return_percent,

    "market_divergence": market_divergence,

    "volume_ratio": volume_ratio,

    "return_zscore": volume_zscore,

    "company_event_present":
        company_event_present
}


# ==========================================
# 12. ATTRIBUTION
# ==========================================

attribution = calculate_attribution(
    attribution_row
)


# ==========================================
# 13. GENERATE EXPLANATION
# ==========================================

explanation = generate_explanation(
    attribution_row,
    attribution
)


# ==========================================
# 14. DISPLAY
# ==========================================

print("\nEXPLAINABLE ATTRIBUTION")
print("======================================")

print("Date:", date)
print("Stock:", symbol)
print("Sector:", sector_name)

print("\nStock return:")
print(round(stock_return, 4), "%")

print("\nSector return:")
print(round(sector_return, 4), "%")

print("\nNIFTY return:")
print(round(market_return_percent, 4), "%")

print("\nVolume ratio:")
print(round(volume_ratio, 4))

print("\nCompany event:")
print(company_event_present)

print("\nPrimary cause:")
print(attribution["primary_cause"])

print("\nRule-based attribution score:")
print(
    attribution["attribution_confidence"],
    "%"
)

print("\nExplanation:")
print("--------------------------------------")
print(explanation)