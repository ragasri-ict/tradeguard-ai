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

from backend.data.company_events import CompanyEvents


# --------------------------------
# Load company events
# --------------------------------

events = CompanyEvents()


# --------------------------------
# Choose company and date
# --------------------------------

symbol = "TCS"
date = "2025-01-17"


# --------------------------------
# Get events
# --------------------------------

result = events.get_events(
    symbol,
    date
)


# --------------------------------
# Display
# --------------------------------

print("\nCompany Events")
print("--------------------------------------")

print("Company:", symbol)
print("Date:", date)

print("\nEvents found:")

print(result)