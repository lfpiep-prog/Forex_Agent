import pytest
from unittest.mock import patch, MagicMock
from execution.notifier import DiscordNotifier

@pytest.fixture
def mock_requests_post():
    with patch("execution.notifier.requests.post") as mock_post:
        yield mock_post

def test_notifier_initialization_with_url():
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    assert notifier.enabled is True

def test_notifier_initialization_without_url():
    # Ensure env var is not set or cleared for this test
    with patch.dict("os.environ", {}, clear=True):
        notifier = DiscordNotifier()
        assert notifier.enabled is False

def test_send_message(mock_requests_post):
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    notifier.send_message("Hello World")
    
    mock_requests_post.assert_called_once()
    args, kwargs = mock_requests_post.call_args
    assert kwargs['json']['content'] == "Hello World"
    assert kwargs['json']['username'] == "Forex Agent"

def test_send_trade_alert(mock_requests_post):
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    
    signal = {
        'direction': 'LONG',
        'symbol': 'EURUSD',
        'entry_price': 1.0500,
        'stop_loss': 1.0450,
        'take_profit': 1.0600,
        'rationale': 'Test Rationale',
        'timestamp': MagicMock()
    }
    order_intent = MagicMock()
    order_intent.quantity = 1000
    
    result = MagicMock()
    result.status = "FILLED"
    result.order_id = "ORDER-123"
    
    notifier.send_trade_alert(signal, order_intent, result)
    
    mock_requests_post.assert_called_once()
    args, kwargs = mock_requests_post.call_args
    embed = kwargs['json']['embeds'][0]
    
    assert "COMPLETED: LONG EURUSD" in embed['title']
    assert embed['color'] == 5763719 # Green
    
    fields = {f['name']: f['value'] for f in embed['fields']}
    assert fields['Status'] == "FILLED"
    assert fields['Size'] == "1000"

def test_send_error(mock_requests_post):
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    notifier.send_error("Something broke")
    
    mock_requests_post.assert_called_once()
    embed = mock_requests_post.call_args[1]['json']['embeds'][0]
    assert "CRITICAL ERROR" in embed['title']
    assert embed['description'] == "Something broke"

def test_send_close_alert_profit(mock_requests_post):
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    
    trade = {
        'direction': 'LONG',
        'symbol': 'USDJPY',
        'entry_price': 150.00,
        'exit_price': 151.00,
        'quantity': 10000,
        'broker_order_id': 'ORDER-456'
    }
    
    notifier.send_close_alert(trade, pnl=100.0)
    
    mock_requests_post.assert_called_once()
    embed = mock_requests_post.call_args[1]['json']['embeds'][0]
    assert "CLOSED: LONG USDJPY" in embed['title']
    assert embed['color'] == 5763719  # Green
    
    fields = {f['name']: f['value'] for f in embed['fields']}
    assert fields['PnL'] == "+100.00"

def test_send_close_alert_loss(mock_requests_post):
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    
    trade = {'direction': 'SHORT', 'symbol': 'EURUSD'}
    notifier.send_close_alert(trade, pnl=-50.0)
    
    embed = mock_requests_post.call_args[1]['json']['embeds'][0]
    assert embed['color'] == 15548997  # Red
    
    fields = {f['name']: f['value'] for f in embed['fields']}
    assert fields['PnL'] == "-50.00"

def test_send_daily_summary(mock_requests_post):
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    
    summary = {
        'date': '2026-01-25',
        'total_trades': 5,
        'wins': 3,
        'losses': 2,
        'total_pnl': 150.0,
        'equity': 10150.0,
        'win_rate': 60.0
    }
    
    notifier.send_daily_summary(summary)
    
    mock_requests_post.assert_called_once()
    embed = mock_requests_post.call_args[1]['json']['embeds'][0]
    assert "Daily Summary" in embed['title']
    assert "2026-01-25" in embed['title']
    
    fields = {f['name']: f['value'] for f in embed['fields']}
    assert fields['Total Trades'] == "5"
    assert fields['Wins'] == "3"
    assert "+150.00" in fields['📈 PnL']

