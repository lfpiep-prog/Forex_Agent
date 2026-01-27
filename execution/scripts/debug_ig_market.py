from dotenv import load_dotenv
load_dotenv()
from execution.brokers.ig_broker import IGBroker
import json
import logging

logging.basicConfig(level=logging.INFO)
broker = IGBroker()
broker.connect()

epic = "CS.D.USDJPY.MINI.IP"
print(f"Fetching details for {epic}...")

# IG API v3 market details
details = broker.ig_service.fetch_market_by_epic(epic)

# Print relevant rules
if details:
    print("\n--- Market Details ---")
    inst = details.get('instrument', {})
    dealing = details.get('dealingRules', {})
    
    print(f"Name: {inst.get('name')}")
    print(f"Currency: {inst.get('currencies')}")
    print(f"Lot Size: {inst.get('lotSize')}")
    print(f"Contract Size: {inst.get('contractSize')}")
    print(f"Type: {inst.get('type')}")
    
    print("\n--- Dealing Rules ---")
    print(json.dumps(dealing, indent=2))
    
    print("\n--- Snapshot ---")
    snap = details.get('snapshot', {})
    print(f"Bid: {snap.get('bid')}")
    print(f"Offer: {snap.get('offer')}")
else:
    print("Failed to fetch details.")
