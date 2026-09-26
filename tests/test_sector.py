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


file_path = "data/raw/sector_data.csv"

df = pd.read_csv(file_path)


print("\nSector Data")

print("----------------------")

print("Rows:", len(df))

print("Columns:", df.columns.tolist())


print("\nFirst 10 rows:")

print(df.head(10))


print("\nSectors:")

print(df["Index Name"].unique())


print("\nDate range:")

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

print("Start:", df["Date"].min())

print("End:", df["Date"].max())