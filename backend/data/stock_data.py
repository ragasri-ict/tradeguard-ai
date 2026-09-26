import pandas as pd


class StockData:

    def __init__(self, file_path="data/raw/stock_data.csv"):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.file_path)

        # Remove extra spaces from column names
        self.data.columns = self.data.columns.str.strip()

        # Convert date
        self.data["Date"] = pd.to_datetime(
            self.data["Date"],
            errors="coerce"
        )

        # Convert numeric columns
        numeric_columns = [
            "Prev Close",
            "Open Price",
            "High Price",
            "Low Price",
            "Last Price",
            "Close Price",
            "Average Price",
            "Total Traded Quantity",
            "No. of Trades",
            "Deliverable Qty",
            "% Dly Qt to Traded Qty"
        ]

        for column in numeric_columns:
            if column in self.data.columns:
                self.data[column] = (
                    self.data[column]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("₹", "", regex=False)
                )

                self.data[column] = pd.to_numeric(
                    self.data[column],
                    errors="coerce"
                )

        return self.data

    def get_data(self):

        if self.data is None:
            self.load_data()

        return self.data

    def get_stock(self, symbol):

        df = self.get_data()

        return df[
            df["Symbol"].str.strip() == symbol
        ].copy()

    def get_detector_data(self, symbol):

        df = self.get_stock(symbol)

        detector_data = df[
            [
                "Date",
                "Symbol",
                "Close Price",
                "Total Traded Quantity"
            ]
        ].copy()

        detector_data = detector_data.rename(
            columns={
                "Close Price": "Close",
                "Total Traded Quantity": "Volume"
            }
        )

        return detector_data