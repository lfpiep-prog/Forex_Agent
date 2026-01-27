from fastapi.testclient import TestClient
from execution.macro_server.main import app
from execution.core.database import get_db, Base, engine
from execution.core.models import TradeResult
from sqlalchemy.orm import Session
from datetime import datetime

# Setup Test Database
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = Session(bind=engine)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_dashboard_endpoint():
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert "Forex Agent Dashboard" in response.text
    assert "Trade History" not in response.text # My simple html doesn't have "Trade History" text explicit, wait. 
    # It has <h1>Forex Agent Dashboard 📈</h1>
    
def test_dashboard_content_with_trades():
    # Insert dummy trade
    db = Session(bind=engine)
    trade = TradeResult(
        symbol="USDJPY",
        direction="LONG",
        entry_price=150.00,
        quantity=10000,
        status="OPEN",
        timestamp=datetime.utcnow()
    )
    db.add(trade)
    db.commit()
    db.close()
    
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert "USDJPY" in response.text
    assert "150.00" in response.text
    assert "LONG" in response.text
