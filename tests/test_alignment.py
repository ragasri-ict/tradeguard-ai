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


# --------------------------------
# Load data
# --------------------------------

stock = StockData()
market = MarketData()
sector = SectorData()


# --------------------------------
# Choose stock
# --------------------------------

symbol = "TCS"
sector_name = "NIFTY IT"
date = "2025-01-10"


# --------------------------------
# Get stock data
# --------------------------------

stock_data = stock.get_stock(symbol)

stock_data["Date"] = pd.to_datetime(
    stock_data["Date"]
)

target_date = pd.to_datetime(date)

row = stock_data[
    stock_data["Date"] == target_date
]


if row.empty:

    print("Stock data not available for this date.")

else:

    current_close = float(
        row.iloc[0]["Close Price"]
    )

    # Find previous trading day
    previous_rows = stock_data[
        stock_data["Date"] < target_date
    ]

    if previous_rows.empty:

        print("Previous stock data not available.")

    else:

        previous_close = float(
            previous_rows.iloc[-1]["Close Price"]
        )

        # Calculate stock return
        stock_return = (
            (current_close - previous_close)
            / previous_close
        ) * 100


        # --------------------------------
        # Get market return
        # --------------------------------

        market_return = market.get_market_return(
            date
        )

        if market_return is not None:
            market_return = market_return * 100


        # --------------------------------
        # Get sector return
        # --------------------------------

        sector_return = sector.get_sector_return(
            sector_name,
            date
        )


        # --------------------------------
        # Display
        # --------------------------------

        print("\nStock / Market / Sector Alignment")
        print("--------------------------------------")

        print("Date:", date)
        print("Stock:", symbol)
        print("Sector:", sector_name)

        print("\nStock return:")
        print(round(stock_return, 4), "%")

        print("\nSector return:")
        print(round(sector_return, 4), "%")

        print("\nMarket return:")
        print(round(market_return, 4), "%")