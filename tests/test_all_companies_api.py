import json
from urllib.request import urlopen
from urllib.parse import quote


BASE_URL = "http://127.0.0.1:8000"

COMPANIES = [
    "TCS",
    "HDFCBANK",
    "ITC",
    "M&M",
    "SUNPHARMA",
    "TATASTEEL"
]

DATE = "2025-01-17"


print("\nFINAL API TEST - ALL COMPANIES")
print("======================================")

passed = 0
failed = 0


for symbol in COMPANIES:

    url = (
        f"{BASE_URL}/attribution/"
        f"{quote(symbol, safe='')}/{DATE}"
    )

    print(f"\nTesting: {symbol}")

    try:

        with urlopen(url, timeout=30) as response:

            status_code = response.status

            data = json.loads(
                response.read().decode("utf-8")
            )


        if status_code != 200:

            print(
                "FAILED - HTTP status:",
                status_code
            )

            failed += 1

            continue


        if "error" in data:

            print(
                "FAILED - API error:",
                data["error"]
            )

            failed += 1

            continue


        required_sections = [
            "movement",
            "technical",
            "company_events",
            "attribution",
            "explanation",
            "alternative_analysis",
            "historical_matching",
            "counterfactual_analysis"
        ]


        missing = [
            section
            for section in required_sections
            if section not in data
        ]


        if missing:

            print(
                "FAILED - Missing sections:",
                missing
            )

            failed += 1

            continue


        print(
            "HTTP status:",
            status_code
        )

        print(
            "Sector:",
            data["sector"]
        )

        print(
            "Stock return:",
            data["movement"]["stock_return"],
            "%"
        )

        print(
            "Primary cause:",
            data["attribution"]["primary_cause"]
        )

        print(
            "Attribution score:",
            data["attribution"][
                "attribution_confidence"
            ],
            "%"
        )

        print(
            "Company event:",
            data["company_events"]["present"]
        )

        print("PASSED")

        passed += 1


    except Exception as error:

        print(
            "FAILED:",
            error
        )

        failed += 1


print("\n======================================")
print("FINAL TEST SUMMARY")
print("======================================")

print("Passed:", passed)
print("Failed:", failed)
print("Total:", len(COMPANIES))