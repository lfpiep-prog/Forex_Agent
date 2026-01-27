"""
Discord Integration Test Script

Tests all Discord notification functions by sending real messages to configured webhooks.
Run: python -m execution.test_discord_live
"""

import os
import sys

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from execution.notifier import DiscordNotifier, DiscordChannel


def test_webhooks_configured():
    """Verify webhooks are configured."""
    print("\n" + "="*50)
    print("WEBHOOK CONFIGURATION CHECK")
    print("="*50)
    
    webhooks = {
        "DISCORD_WEBHOOK_URL (Main)": os.getenv("DISCORD_WEBHOOK_URL"),
        "DISCORD_WEBHOOK_TRADES": os.getenv("DISCORD_WEBHOOK_TRADES"),
        "DISCORD_WEBHOOK_RISK": os.getenv("DISCORD_WEBHOOK_RISK"),
        "DISCORD_WEBHOOK_HEALTH": os.getenv("DISCORD_WEBHOOK_HEALTH"),
        "DISCORD_WEBHOOK_REPORTS": os.getenv("DISCORD_WEBHOOK_REPORTS"),
    }
    
    all_configured = True
    for name, url in webhooks.items():
        if url and url.startswith("https://discord.com/api/webhooks/"):
            print(f"✅ {name}: Configured")
        elif url:
            print(f"⚠️ {name}: Set but invalid format")
            all_configured = False
        else:
            print(f"❌ {name}: Not set (will fallback to main)")
    
    return all_configured


def test_trade_alert(notifier: DiscordNotifier):
    """Send test trade alert."""
    print("\n📊 Sending Trade Alert...")
    
    from unittest.mock import MagicMock
    
    signal = {
        'direction': 'LONG',
        'symbol': 'EUR/USD',
        'entry_price': 1.0850,
        'stop_loss': 1.0820,
        'take_profit': 1.0900,
        'rationale': '🧪 TEST: EMA crossover signal with bullish momentum',
        'timestamp': datetime.now(timezone.utc)
    }
    
    order_intent = MagicMock()
    order_intent.quantity = 0.10
    
    result = MagicMock()
    result.status = "FILLED"
    result.order_id = "TEST-ORDER-001"
    
    notifier.send_trade_alert(signal, order_intent, result)
    print("   ✅ Trade alert sent to #trade-alerts")


def test_close_alert(notifier: DiscordNotifier):
    """Send test position close alert."""
    print("\n💰 Sending Close Alert...")
    
    trade = {
        'direction': 'LONG',
        'symbol': 'EUR/USD',
        'entry_price': 1.0850,
        'exit_price': 1.0895,
        'quantity': 0.10,
        'broker_order_id': 'TEST-ORDER-001'
    }
    
    notifier.send_close_alert(trade, pnl=45.00)
    print("   ✅ Close alert sent to #trade-alerts")


def test_risk_alert(notifier: DiscordNotifier):
    """Send test risk alert."""
    print("\n🚨 Sending Risk Alert...")
    
    details = {
        'current': '2.5%',
        'limit': '2.0%',
        'action': '🧪 TEST: Trading would be PAUSED'
    }
    
    notifier.send_risk_alert("TEST_DAILY_LOSS_LIMIT", details)
    print("   ✅ Risk alert sent to #risk-alerts")


def test_health_status(notifier: DiscordNotifier):
    """Send test health status."""
    print("\n🟢 Sending Health Status...")
    
    details = {
        'broker': 'IG-DEMO connected',
        'data_feed': 'TwelveData OK',
        'last_candle': datetime.now(timezone.utc).strftime('%H:%M UTC'),
        'db': 'trades.db (test)',
        'uptime': '🧪 TEST'
    }
    
    notifier.send_health_status("OK", details)
    print("   ✅ Health status sent to #system-health")


def test_daily_summary(notifier: DiscordNotifier):
    """Send test daily summary."""
    print("\n📊 Sending Daily Summary...")
    
    summary = {
        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'total_trades': 5,
        'wins': 4,
        'losses': 1,
        'total_pnl': 127.50,
        'equity': 10127.50,
        'win_rate': 80.0,
        'biggest_win': 52.00,
        'biggest_loss': -18.00,
        'errors_count': 0
    }
    
    notifier.send_daily_summary(summary)
    print("   ✅ Daily summary sent to #daily-report")


def test_weekly_summary(notifier: DiscordNotifier):
    """Send test weekly summary."""
    print("\n📅 Sending Weekly Summary...")
    
    summary = {
        'week': 'W04 2026',
        'total_trades': 25,
        'total_pnl': 523.00,
        'win_rate': 72.0,
        'max_drawdown': 1.8,
        'risk_events': 1,
        'errors_count': 0
    }
    
    notifier.send_weekly_summary(summary)
    print("   ✅ Weekly summary sent to #weekly-report")


def test_error_alert(notifier: DiscordNotifier):
    """Send test error alert."""
    print("\n🚨 Sending Error Alert...")
    
    notifier.send_error("🧪 TEST: This is a test error alert - everything is working fine!")
    print("   ✅ Error alert sent to #system-health")


def run_all_tests():
    """Run all Discord integration tests."""
    print("\n" + "="*50)
    print("🧪 DISCORD LIVE INTEGRATION TEST")
    print(f"   Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*50)
    
    # Check configuration
    test_webhooks_configured()
    
    # Create notifier
    notifier = DiscordNotifier()
    
    if not notifier.enabled:
        print("\n❌ ERROR: DiscordNotifier is disabled. Check DISCORD_WEBHOOK_URL in .env")
        return False
    
    print("\n" + "-"*50)
    print("SENDING TEST MESSAGES TO DISCORD")
    print("-"*50)
    
    try:
        # Test each channel
        test_trade_alert(notifier)
        test_close_alert(notifier)
        test_risk_alert(notifier)
        test_health_status(notifier)
        test_daily_summary(notifier)
        test_weekly_summary(notifier)
        test_error_alert(notifier)
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED!")
        print("   Check your Discord channels for the test messages.")
        print("="*50 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during tests: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
