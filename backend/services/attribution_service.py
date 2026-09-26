import pandas as pd

from backend.data.stock_data import StockData
from backend.data.market_data import MarketData
from backend.data.sector_data import SectorData
from backend.data.company_events import CompanyEvents

from backend.models.event_detector import EventDetector
from backend.models.attribution import calculate_attribution
from backend.models.explainability import generate_explanation
from backend.models.historical_match import match_historical_events
from backend.models.counterfactual import run_all_counterfactuals
from backend.models.contradiction import analyze_alternative_causes


class AttributionService:

    def __init__(self):

        self.stock = StockData()
        self.market = MarketData()
        self.sector = SectorData()
        self.events = CompanyEvents()

        self.detector = EventDetector()

    def analyze(self, symbol, sector_name, date):

        target_date = pd.to_datetime(date)

        # ==========================================
        # 1. STOCK DATA
        # ==========================================

        stock_data = self.stock.get_stock(symbol).copy()

        if stock_data.empty:
            return {
                "error": f"No stock data found for {symbol}"
            }

        stock_data["Date"] = pd.to_datetime(
            stock_data["Date"],
            errors="coerce"
        )

        stock_data["Close Price"] = pd.to_numeric(
            stock_data["Close Price"],
            errors="coerce"
        )

        stock_data["Total Traded Quantity"] = pd.to_numeric(
            stock_data["Total Traded Quantity"],
            errors="coerce"
        )

        stock_data = stock_data.sort_values(
            "Date"
        ).reset_index(drop=True)

        # Stock return
        stock_data["stock_return"] = (
            stock_data["Close Price"]
            .pct_change()
            * 100
        )

        # Previous 5-day average volume
        previous_volume_average = (
            stock_data["Total Traded Quantity"]
            .shift(1)
            .rolling(window=5)
            .mean()
        )

        stock_data["volume_ratio"] = (
            stock_data["Total Traded Quantity"]
            / previous_volume_average
        )

        # ==========================================
        # 2. VOLUME Z-SCORE
        # ==========================================

        detector_data = self.stock.get_detector_data(
            symbol
        )

        detector_result = self.detector.detect(
            detector_data
        )

        detector_result["Date"] = pd.to_datetime(
            detector_result["Date"],
            errors="coerce"
        )

        volume_features = detector_result[
            [
                "Date",
                "volume_zscore"
            ]
        ].copy()

        stock_data = stock_data.merge(
            volume_features,
            on="Date",
            how="left"
        )

        # ==========================================
        # 3. NIFTY 50
        # ==========================================

        market_data = self.market.get_data().copy()

        market_data["Date"] = pd.to_datetime(
            market_data["Date"],
            errors="coerce"
        )

        market_data["Close"] = pd.to_numeric(
            market_data["Close"],
            errors="coerce"
        )

        market_data = market_data.sort_values(
            "Date"
        ).reset_index(drop=True)

        market_data["nifty_return"] = (
            market_data["Close"]
            .pct_change()
            * 100
        )

        market_features = market_data[
            [
                "Date",
                "nifty_return"
            ]
        ].copy()

        # ==========================================
        # 4. SECTOR
        # ==========================================

        sector_data = self.sector.get_sector(
            sector_name
        ).copy()

        if sector_data.empty:
            return {
                "error":
                    f"No sector data found for {sector_name}"
            }

        sector_data["Date"] = pd.to_datetime(
            sector_data["Date"],
            errors="coerce"
        )

        sector_data["sector_return"] = pd.to_numeric(
            sector_data["sector_return"],
            errors="coerce"
        )

        sector_features = sector_data[
            [
                "Date",
                "sector_return"
            ]
        ].copy()

        # ==========================================
        # 5. MERGE STOCK + MARKET + SECTOR
        # ==========================================

        analysis_data = stock_data.merge(
            market_features,
            on="Date",
            how="left"
        )

        analysis_data = analysis_data.merge(
            sector_features,
            on="Date",
            how="left"
        )

        # ==========================================
        # 6. MARKET DIVERGENCE
        # ==========================================

        analysis_data["market_divergence"] = (
            analysis_data["stock_return"]
            - analysis_data["nifty_return"]
        )

        # ==========================================
        # 7. CLEAN REQUIRED DATA
        # ==========================================

        required_columns = [
            "Date",
            "Symbol",
            "stock_return",
            "volume_ratio",
            "volume_zscore",
            "nifty_return",
            "sector_return",
            "market_divergence"
        ]

        analysis_data = analysis_data[
            required_columns
        ].copy()

        # ==========================================
        # 8. TARGET DATE
        # ==========================================

        target_rows = analysis_data[
            analysis_data["Date"] == target_date
        ]

        if target_rows.empty:
            return {
                "error":
                    f"No complete market/sector data found "
                    f"for {symbol} on {date}"
            }

        target = target_rows.iloc[0]

        # ==========================================
        # 9. COMPANY EVENT
        # ==========================================

        company_events = self.events.get_events(
            symbol,
            date
        )

        company_event_present = (
            not company_events.empty
        )

        # ==========================================
        # 10. ATTRIBUTION INPUT
        # ==========================================

        attribution_row = {

            "stock_return":
                float(target["stock_return"]),

            "sector_return":
                float(target["sector_return"]),

            "nifty_return":
                float(target["nifty_return"]),

            "market_divergence":
                float(target["market_divergence"]),

            "volume_ratio":
                float(target["volume_ratio"]),

            "volume_zscore":
                float(target["volume_zscore"]),

            "company_event_present":
                company_event_present
        }

        # ==========================================
        # 11. ATTRIBUTION
        # ==========================================

        attribution = calculate_attribution(
            attribution_row
        )

        # ==========================================
        # 12. EXPLANATION
        # ==========================================

        explanation = generate_explanation(
            attribution_row,
            attribution
        )

        # ==========================================
        # 13. ALTERNATIVE / CONTRADICTION
        # ==========================================

        alternatives = analyze_alternative_causes(
            attribution_row,
            attribution
        )

        # ==========================================
        # 14. HISTORICAL MATCHING
        # ==========================================

        historical_data = analysis_data.dropna(
            subset=[
                "stock_return",
                "volume_ratio",
                "volume_zscore",
                "nifty_return",
                "sector_return",
                "market_divergence"
            ]
        ).copy()

        historical_matches = match_historical_events(
            historical_data,
            max_history=100,
            top_matches=5,
            minimum_history=20
        )

        historical_target = historical_matches[
            historical_matches["Date"] == target_date
        ]

        historical_result = {}

        if not historical_target.empty:

            historical_row = (
                historical_target.iloc[0]
            )

            historical_result = {

                "historical_match_score":
                    historical_row[
                        "historical_match_score"
                    ],

                "historical_match_count":
                    int(
                        historical_row[
                            "historical_match_count"
                        ]
                    ),

                "historical_avg_return":
                    historical_row[
                        "historical_avg_return"
                    ],

                "historical_median_return":
                    historical_row[
                        "historical_median_return"
                    ],

                "expected_reaction":
                    historical_row[
                        "expected_reaction"
                    ],

                "historical_match_dates":
                    historical_row[
                        "historical_match_dates"
                    ],

                "historical_match_returns":
                    historical_row[
                        "historical_match_returns"
                    ]
            }

        # ==========================================
        # 15. COUNTERFACTUAL
        # ==========================================

        counterfactual_results = (
            run_all_counterfactuals(
                attribution_row
            )
        )

        # ==========================================
        # 16. COMPANY EVENTS FOR RESPONSE
        # ==========================================

        event_records = []

        if not company_events.empty:

            event_records = (
                company_events
                .fillna("")
                .to_dict(
                    orient="records"
                )
            )

        # ==========================================
        # 17. FINAL RESPONSE
        # ==========================================

        return {

            "date": date,

            "symbol": symbol,

            "sector": sector_name,

            "movement": {

                "stock_return":
                    round(
                        float(
                            target["stock_return"]
                        ),
                        4
                    ),

                "sector_return":
                    round(
                        float(
                            target["sector_return"]
                        ),
                        4
                    ),

                "nifty_return":
                    round(
                        float(
                            target["nifty_return"]
                        ),
                        4
                    ),

                "market_divergence":
                    round(
                        float(
                            target[
                                "market_divergence"
                            ]
                        ),
                        4
                    )
            },

            "technical": {

                "volume_ratio":
                    round(
                        float(
                            target["volume_ratio"]
                        ),
                        4
                    ),

                "volume_zscore":
                    round(
                        float(
                            target["volume_zscore"]
                        ),
                        4
                    )
            },

            "company_events": {

                "present":
                    company_event_present,

                "events":
                    event_records
            },

            "attribution":
                attribution,

            "explanation":
                explanation,

            "alternative_analysis":
                alternatives,

            "historical_matching":
                historical_result,

            "counterfactual_analysis":
                counterfactual_results
        }