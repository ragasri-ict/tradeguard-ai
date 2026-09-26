import pandas as pd


class CompanyEvents:

    def __init__(
        self,
        file_path="data/raw/events/company_events.csv"
    ):
        self.file_path = file_path
        self.data = None

    def load_data(self):

        self.data = pd.read_csv(
            self.file_path
        )

        # Clean column names
        self.data.columns = (
            self.data.columns
            .str.strip()
        )

        # Convert date
        self.data["date"] = pd.to_datetime(
            self.data["date"],
            errors="coerce"
        )

        # Clean symbol
        if "symbol" in self.data.columns:
            self.data["symbol"] = (
                self.data["symbol"]
                .astype(str)
                .str.strip()
            )

        return self.data

    def get_data(self):

        if self.data is None:
            self.load_data()

        return self.data

    def get_events(self, symbol, date):

        df = self.get_data()

        date = pd.to_datetime(date)

        result = df[
            (df["symbol"] == symbol)
            &
            (df["date"] == date)
        ].copy()

        return result