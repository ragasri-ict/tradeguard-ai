from backend.data.market_data import MarketData


class MarketService:

    def __init__(self):

        self.market_data = MarketData()

    def get_market_movement(self, date):

        market_return = self.market_data.get_market_return(date)

        if market_return is None:

            return {
                "date": str(date),
                "market_return": None,
                "message": "NIFTY data not available for this date"
            }

        return {
            "date": str(date),
            "market_return": round(market_return * 100, 2),
            "market_return_decimal": round(market_return, 6)
        }