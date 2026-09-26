import pandas as pd

from backend.models.event_detector import EventDetector


def test_event_detection():

    data = pd.read_csv("data/sample_stock_data.csv")

    detector = EventDetector()

    result = detector.detect(data)

    print("\nDetected Events:")
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
        ]
    )

    assert result["is_anomaly"].any()