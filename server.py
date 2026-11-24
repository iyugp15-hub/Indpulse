from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dhanhq import DhanContext, dhanhq
import os

app = FastAPI(title="IndiaPulse Live Market Website")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def serve_home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

@app.get("/api/live-sync")
def live_sync(
    access_token: str = Header(..., alias="access-token"),
    client_id: str = Header(..., alias="client-id"),
):
    try:
        ctx = DhanContext(client_id, access_token)
        dhan = dhanhq(ctx)
        holdings_res = dhan.get_holdings()
        trades_res = dhan.get_trade_book()
        holdings = holdings_res.get("data", holdings_res) if isinstance(holdings_res, dict) else holdings_res
        trades = trades_res.get("data", trades_res) if isinstance(trades_res, dict) else trades_res
        return {
            "data": holdings if isinstance(holdings, list) else [],
            "trades": trades if isinstance(trades, list) else [],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
