from backend.data.stock_data import StockData


stock = StockData()

df = stock.get_data()

print("\nStock Dataset")
print("----------------------")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nCompanies:")
print(df["Symbol"].value_counts())

print("\nSeries:")
print(df["Series"].value_counts())

print("\nDate range:")
print(df["Date"].min())
print(df["Date"].max())

print("\nFirst 5 rows:")
print(df.head())
