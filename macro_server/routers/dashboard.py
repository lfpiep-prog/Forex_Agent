from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from core.models import TradeResult

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Simple Server-Side Rendered Dashboard using basic HTML/CSS.
    """
    trades = db.query(TradeResult).order_by(TradeResult.timestamp.desc()).limit(50).all()
    
    # Simple CSS for dark mode
    css = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #d4d4d4; padding: 20px; }
        h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #333; }
        th { background-color: #252526; color: #fff; }
        tr:hover { background-color: #2d2d30; }
        .status-open { color: #f1c40f; font-weight: bold; }
        .status-closed { color: #95a5a6; }
        .status-profit { color: #2ecc71; }
        .status-loss { color: #e74c3c; }
        .card { background-color: #252526; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .long { color: #2ecc71; font-weight: bold; }
        .short { color: #e74c3c; font-weight: bold; }
    </style>
    """
    
    # Calculate some stats
    total_trades = len(trades)
    
    rows = ""
    for t in trades:
        # Determine Color for Direction
        dir_class = "long" if t.direction == "LONG" else "short"
        
        # Determine Color for Status
        status_color = "#ccc"
        if t.status == "OPEN": status_color = "#f1c40f"
        elif t.status == "CLOSED": status_color = "#95a5a6"
        elif t.status == "CANCELLED": status_color = "#e74c3c"
        
        # Calculate PnL Color if closed
        pnl_display = "-"
        if t.pnl is not None:
             pnl_class = "status-profit" if t.pnl >= 0 else "status-loss"
             pnl_display = f"<span class='{pnl_class}'>{t.pnl:.2f}</span>"
        
        rows += f"""
        <tr>
            <td>{t.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
            <td>{t.symbol}</td>
            <td class="{dir_class}">{t.direction}</td>
            <td>{t.entry_price:.5f}</td>
            <td>{t.quantity}</td>
            <td style="color:{status_color}">{t.status}</td>
            <td>{pnl_display}</td>
            <td>{t.broker_order_id or '-'}</td>
        </tr>
        """
        
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forex Agent Dashboard</title>
        <meta http-equiv="refresh" content="60"> <!-- Auto-refresh every 60s -->
        {css}
    </head>
    <body>
        <div class="card">
            <h1>Forex Agent Dashboard 📈</h1>
            <p>Showing last {total_trades} trades.</p>
        </div>
        
        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th>Time (UTC)</th>
                        <th>Symbol</th>
                        <th>Direction</th>
                        <th>Entry Price</th>
                        <th>Size</th>
                        <th>Status</th>
                        <th>PnL</th>
                        <th>Order ID</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
