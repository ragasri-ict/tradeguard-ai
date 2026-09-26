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

from backend.models.attribution import calculate_attribution


# --------------------------------
# Test data
# --------------------------------

row = {
    "stock_return": -1.9495,
    "sector_return": -2.6780,
    "nifty_return": -0.4659,
    "market_divergence": -1.4836,
    "volume_ratio": 1.5,
    "return_zscore": 1.2,
    "company_event_present": True
}


# --------------------------------
# Calculate attribution
# --------------------------------

result = calculate_attribution(row)


# --------------------------------
# Display result
# --------------------------------

print("\nCAUSE ATTRIBUTION")
print("======================================")

print(
    "Company event score:",
    result["company_event_score"]
)

print(
    "Sector movement score:",
    result["sector_movement_score"]
)

print(
    "Market movement score:",
    result["market_movement_score"]
)

print(
    "Technical flow score:",
    result["technical_flow_score"]
)

print(
    "Stock-specific move score:",
    result["stock_specific_move_score"]
)

print(
    "Unknown score:",
    result["unknown_score"]
)

print("\nPrimary cause:")
print(result["primary_cause"])

print("\nAttribution confidence:")
print(
    result["attribution_confidence"],
    "%"
)