import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

URLSCAN_API_KEY = os.getenv("URLSCAN_API_KEY")
URLSCAN_SUBMIT_URL = "https://urlscan.io/api/v1/scan/"

app = FastAPI(
    title="Broken Link Scanner API",
    description="Scan links using urlscan.io and return basic scan info.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {
        "message": "Broken Link Scanner API 🔍",
        "usage": "POST /scan-link with JSON { 'url': 'https://example.com' }"
    }

@app.post("/scan-link")
async def scan_link(body: ScanRequest):
    if not URLSCAN_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="URLSCAN_API_KEY is not set on the server."
        )

    headers = {
        "API-Key": URLSCAN_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "url": body.url,
        "visibility": "public"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(URLSCAN_SUBMIT_URL, json=payload, headers=headers)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Failed to contact urlscan.io: {str(e)}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"urlscan.io error: {resp.text}"
        )

    data = resp.json()

    # Tunarudisha info muhimu tu
    return {
        "submitted_url": body.url,
        "scan_id": data.get("uuid"),
        "result_url": data.get("result"),
        "api_result": data
    }
