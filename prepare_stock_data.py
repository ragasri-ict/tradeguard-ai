import pandas as pd

INPUT_FILE = "data/raw/stock_data.csv"
OUTPUT_FILE = "data/raw/stock_data_prototype.csv"

# Our 6 prototype companies
COMPANIES = [
    "M&M",
    "HDFCBANK",
    "ITC",
    "SUNPHARMA",
    "TCS",
    "TATASTEEL"
]

print("\n================================")
print("PREPARING STOCK DATA")
print("================================\n")

print("Reading stock data...")

df = pd.read_csv(INPUT_FILE)

print("Original rows:", len(df))

# ---------------------------------------
# Convert date
# ---------------------------------------

df["TIMESTAMP"] = pd.to_datetime(
    df["TIMESTAMP"],
    errors="coerce"
)

# ---------------------------------------
# Keep only 2023-2025
# ---------------------------------------

df = df[
    (df["TIMESTAMP"] >= "2023-01-01") &
    (df["TIMESTAMP"] <= "2025-12-31")
]

print("Rows after date filtering:", len(df))

# ---------------------------------------
# Keep only selected companies
# ---------------------------------------

df = df[
    df["SYMBOL"].isin(COMPANIES)
]

print("Rows after company filtering:", len(df))

# ---------------------------------------
# Keep useful columns
# ---------------------------------------

df = df[
    [
        "SYMBOL",
        "SERIES",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "PREVCLOSE",
        "TOTTRDQTY",
        "TOTTRDVAL",
        "TIMESTAMP",
        "TOTALTRADES",
        "ISIN"
    ]
]

# ---------------------------------------
# Sort
# ---------------------------------------

df = df.sort_values(
    ["SYMBOL", "TIMESTAMP"]
).reset_index(drop=True)

# ---------------------------------------
# Save
# ---------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n================================")
print("STOCK DATA PREPARATION COMPLETE")
print("================================")

print("\nFinal rows:", len(df))

print("\nCompanies found:")

for company in sorted(df["SYMBOL"].unique()):
    print("✓", company)

print("\nDate range:")
print("Start:", df["TIMESTAMP"].min())
print("End:", df["TIMESTAMP"].max())

print("\nCreated:")
print("✓", OUTPUT_FILE)