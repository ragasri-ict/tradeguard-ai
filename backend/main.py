from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.services.attribution_service import (
    AttributionService
)


# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="AI-Powered Market Event Attribution",
    description=(
        "Explainable market event attribution "
        "system for Indian equities"
    ),
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# SERVICE
# ==========================================

service = AttributionService()


# ==========================================
# COMPANY-SECTOR MAPPING
# ==========================================

SECTOR_MAP = {

    "M&M": "NIFTY AUTO",

    "HDFCBANK": "NIFTY BANK",

    "ITC": "NIFTY FMCG",

    "SUNPHARMA": "NIFTY HEALTHCARE",

    "TCS": "NIFTY IT",

    "TATASTEEL": "NIFTY METAL"
}


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():

    return {
        "message":
            "AI-Powered Market Event Attribution API",

        "status":
            "running"
    }


# ==========================================
# HEALTH
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==========================================
# COMPANIES
# ==========================================

@app.get("/companies")
def companies():

    return {

        "companies": [

            {
                "symbol": "M&M",
                "company": "Mahindra & Mahindra",
                "sector": "NIFTY AUTO"
            },

            {
                "symbol": "HDFCBANK",
                "company": "HDFC Bank",
                "sector": "NIFTY BANK"
            },

            {
                "symbol": "ITC",
                "company": "ITC",
                "sector": "NIFTY FMCG"
            },

            {
                "symbol": "SUNPHARMA",
                "company": "Sun Pharma",
                "sector": "NIFTY HEALTHCARE"
            },

            {
                "symbol": "TCS",
                "company": "TCS",
                "sector": "NIFTY IT"
            },

            {
                "symbol": "TATASTEEL",
                "company": "Tata Steel",
                "sector": "NIFTY METAL"
            }
        ]
    }


# ==========================================
# ATTRIBUTION
# ==========================================

@app.get(
    "/attribution/{symbol}/{date}"
)
def attribution(
    symbol: str,
    date: str
):

    # Convert URL symbol to uppercase
    # so /tcs and /TCS both work.
    symbol = symbol.upper()

    if symbol not in SECTOR_MAP:

        return {
            "error":
                f"Unsupported stock symbol: {symbol}"
        }

    return service.analyze(
        symbol,
        SECTOR_MAP[symbol],
        date
    )