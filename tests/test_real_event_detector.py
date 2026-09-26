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

from backend.data.stock_data import StockData
from backend.models.event_detector import EventDetector


stock = StockData()

# Use TCS first
data = stock.get_detector_data("TCS")

print("\nReal TCS Data")
print("----------------------")

print("Rows:", len(data))

print("Columns:", data.columns.tolist())

print(data.head())


detector = EventDetector()

result = detector.detect(data)


print("\nEvent Detection Result")
print("----------------------")

print(
    result[
        [
            "Date",
            "Symbol",
            "Close",
            "Volume",
            "price_return",
            "volume_zscore",
            "is_anomaly"
        ]
    ].tail(20)
)


print("\nTotal anomalies:")

print(result["is_anomaly"].sum())