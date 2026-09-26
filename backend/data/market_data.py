import pandas as pd


class MarketData:

    def __init__(self, file_path="data/raw/nifty/nifty_data.csv"):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        """
        Load NIFTY 50 historical data.
        """

        self.data = pd.read_csv(self.file_path)

        return self.data

    def get_data(self):

        if self.data is None:
            self.load_data()

        return self.data

    def get_market_return(self, date):

        df = self.get_data().copy()

        # Convert date column
        df["Date"] = pd.to_datetime(df["Date"])

        # Convert requested date
        date = pd.to_datetime(date)

        # Find the selected date
        current = df[df["Date"] == date]

        if current.empty:
            return None

        # Find previous trading day
        previous = df[df["Date"] < date].tail(1)

        if previous.empty:
            return None

        current_close = float(current.iloc[0]["Close"])
        previous_close = float(previous.iloc[0]["Close"])

        market_return = (
            (current_close - previous_close)
            / previous_close
        )

        return market_return