import sys
import os
from dotenv import load_dotenv

# Load .env
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv()

from execution.brokers.ig_broker import IGBroker

def test_connection():
    print("--- Testing IG Connection ---")
    broker = IGBroker()
    print(f"User: {broker.username}") 
    # Mask password
    masked_pw = broker.password[:2] + "****" + broker.password[-2:] if broker.password and len(broker.password) > 4 else "****"
    print(f"Pass: {masked_pw}")
    print(f"Key:  {broker.api_key[:4]}...{broker.api_key[-4:]}")
    print(f"Type: {broker.acc_type}")
    
    if broker.connect():
        print("Connected!")
        
        balance = broker.get_balance()
        if balance:
            print(f"Balance Info: {balance}")
        else:
            print("Connected but failed to fetch balance.")
            
    else:
        print("Connection Failed. Check credentials in .env")

if __name__ == "__main__":
    test_connection()
