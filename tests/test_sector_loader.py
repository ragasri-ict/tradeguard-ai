import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from backend.data.sector_data import SectorData


sector = SectorData()

data = sector.get_sector("NIFTY IT")

print("\nNIFTY IT Data")
print("Rows:", len(data))
print("Columns:", list(data.columns))

print("\nFirst 5 rows:")
print(data.head())

test_date = "2025-01-10"

result = sector.get_sector_return(
    "NIFTY IT",
    test_date
)

print("\nTest sector return:")
print(
    "NIFTY IT return on",
    test_date,
    ":",
    result
)