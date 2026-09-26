import pandas as pd
import numpy as np


class EventDetector:

    def __init__(self, price_change_threshold=0.03,
                 volume_zscore_threshold=2.0):

        self.price_change_threshold = price_change_threshold
        self.volume_zscore_threshold = volume_zscore_threshold

    def detect(self, data):

        df = data.copy()

        # Make sure data is sorted by date
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # Calculate daily price return
        df["price_return"] = df["Close"].pct_change()

        # Calculate rolling average volume
        df["volume_mean"] = (
            df["Volume"]
            .rolling(window=5)
            .mean()
        )

        # Calculate rolling standard deviation
        df["volume_std"] = (
            df["Volume"]
            .rolling(window=5)
            .std()
        )

        # Calculate volume z-score
        df["volume_zscore"] = (
            (df["Volume"] - df["volume_mean"])
            / df["volume_std"]
        )

        # Detect unusual price movement
        df["price_anomaly"] = (
            df["price_return"].abs()
            >= self.price_change_threshold
        )

        # Detect unusual volume
        df["volume_anomaly"] = (
            df["volume_zscore"].abs()
            >= self.volume_zscore_threshold
        )

        # Overall anomaly
        df["is_anomaly"] = (
            df["price_anomaly"]
            | df["volume_anomaly"]
        )

        return df