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

from backend.services.market_service import MarketService


service = MarketService()

result = service.get_market_movement("2025-01-10")

print(result)