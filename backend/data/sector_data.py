import pandas as pd


class SectorData:

    def __init__(self, file_path="data/raw/sector_data.csv"):
        self.file_path = file_path
        self.data = None

    def load_data(self):

        self.data = pd.read_csv(self.file_path)

        # Clean column names
        self.data.columns = self.data.columns.str.strip()

        # Convert date
        self.data["Date"] = pd.to_datetime(
            self.data["Date"],
            errors="coerce"
        )

        # Convert numeric columns
        self.data["Close"] = pd.to_numeric(
            self.data["Close"],
            errors="coerce"
        )

        self.data["sector_return"] = pd.to_numeric(
            self.data["sector_return"],
            errors="coerce"
        )

        return self.data

    def get_data(self):

        if self.data is None:
            self.load_data()

        return self.data

    def get_sector(self, sector_name):

        df = self.get_data()

        return df[
            df["Index Name"].str.strip() == sector_name
        ].copy()

    def get_sector_return(self, sector_name, date):

        df = self.get_sector(sector_name)

        date = pd.to_datetime(date)

        row = df[df["Date"] == date]

        if row.empty:
            return None

        return float(
            row.iloc[0]["sector_return"]
        )