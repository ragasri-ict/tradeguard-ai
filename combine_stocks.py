import pandas as pd
import glob
import os

INPUT_FOLDER = "data/raw/stock_2023_2025"
OUTPUT_FILE = "data/raw/stock_data.csv"

files = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))

all_data = []

for file in files:

    print("Reading:", file)

    df = pd.read_csv(file)

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    # Keep only normal equity data
    if "Series" in df.columns:
        df["Series"] = df["Series"].astype(str).str.strip()
        df = df[df["Series"] == "EQ"]

    all_data.append(df)


combined = pd.concat(all_data, ignore_index=True)

# Clean column names
combined.columns = combined.columns.str.strip()

# Remove duplicate rows
combined = combined.drop_duplicates()

# Sort by symbol and date
if "Date" in combined.columns:
    combined["Date"] = pd.to_datetime(
        combined["Date"],
        errors="coerce"
    )

combined = combined.sort_values(
    by=["Symbol", "Date"]
)

combined.to_csv(OUTPUT_FILE, index=False)

print("\n--------------------------------")
print("Stock data combined successfully")
print("--------------------------------")
print("Total rows:", len(combined))
print("Total columns:", len(combined.columns))
print("Companies:")
print(combined["Symbol"].unique())
print("\nCreated:", OUTPUT_FILE)
