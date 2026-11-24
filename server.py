from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json
import os
import urllib.request
import urllib.error

app = FastAPI(title="IndiaPulse Live Market Website")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_dhan(path: str, client_id: str, access_token: str):
    req = urllib.request.Request(
        f"https://api.dhan.co/v2{path}",
        headers={
            "access-token": access_token,
            "client-id": client_id,
            "Accept": "application/json",
            "User-Agent": "IndiaPulse/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

@app.get("/")
def serve_home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

@app.get("/api/live-sync")
def live_sync(
    access_token: str = Header(..., alias="access-token"),
    client_id: str = Header(..., alias="client-id"),
):
    try:
        holdings_res = fetch_dhan("/holdings", client_id, access_token)
        holdings = holdings_res.get("data", holdings_res) if isinstance(holdings_res, dict) else holdings_res
        try:
            trades_res = fetch_dhan("/trades", client_id, access_token)
            trades = trades_res.get("data", trades_res) if isinstance(trades_res, dict) else trades_res
        except Exception:
            trades = []
        return {
            "data": holdings if isinstance(holdings, list) else [],
            "trades": trades if isinstance(trades, list) else [],
        }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(status_code=exc.code, detail=detail or str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
