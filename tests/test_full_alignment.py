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


# --------------------------------
# Load all data
# --------------------------------

stock = StockData()
market = MarketData()
sector = SectorData()
events = CompanyEvents()


# --------------------------------
# Select stock and date
# --------------------------------

symbol = "TCS"
sector_name = "NIFTY IT"
date = "2025-01-17"

target_date = pd.to_datetime(date)


# --------------------------------
# STOCK RETURN
# --------------------------------

stock_data = stock.get_stock(symbol)

stock_data["Date"] = pd.to_datetime(
    stock_data["Date"]
)

current_row = stock_data[
    stock_data["Date"] == target_date
]

previous_rows = stock_data[
    stock_data["Date"] < target_date
]

if current_row.empty:

    print("Stock data not available.")
    exit()

if previous_rows.empty:

    print("Previous stock data not available.")
    exit()


current_close = float(
    current_row.iloc[0]["Close Price"]
)

previous_close = float(
    previous_rows.iloc[-1]["Close Price"]
)

stock_return = (
    (current_close - previous_close)
    / previous_close
) * 100


# --------------------------------
# MARKET RETURN
# --------------------------------

market_return = market.get_market_return(date)

if market_return is not None:
    market_return = market_return * 100


# --------------------------------
# SECTOR RETURN
# --------------------------------

sector_return = sector.get_sector_return(
    sector_name,
    date
)


# --------------------------------
# COMPANY EVENT
# --------------------------------

company_events = events.get_events(
    symbol,
    date
)


# --------------------------------
# DISPLAY
# --------------------------------

print("\nFULL EVENT ALIGNMENT")
print("======================================")

print("Date:", date)
print("Stock:", symbol)
print("Sector:", sector_name)

print("\nStock return:")
print(round(stock_return, 4), "%")

print("\nSector return:")
print(round(sector_return, 4), "%")

print("\nMarket return:")
print(round(market_return, 4), "%")


print("\nCompany events:")

if company_events.empty:

    print("No company event found.")

else:

    print(
        company_events[
            [
                "date",
                "symbol",
                "event_type",
                "subject"
            ]
        ].to_string(index=False)
    )