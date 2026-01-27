import pytest
from unittest.mock import patch, MagicMock
from execution.notifier import DiscordNotifier, DiscordChannel


@pytest.fixture
def mock_requests_post():
    with patch("execution.notifier.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        yield mock_post


@pytest.fixture
def notifier():
    """Create a notifier with test webhook URL."""
    return DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")


class TestDiscordNotifierInit:
    """Tests for DiscordNotifier initialization."""

    def test_initialization_with_url(self):
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
        assert notifier.enabled is True

    def test_initialization_without_url(self):
        with patch.dict("os.environ", {}, clear=True):
            notifier = DiscordNotifier()
            assert notifier.enabled is False

    def test_channel_webhooks_fallback_to_main(self):
        """When channel-specific webhooks are not set, they should fallback to main."""
        with patch.dict("os.environ", {"DISCORD_WEBHOOK_URL": "https://main.webhook"}, clear=True):
            notifier = DiscordNotifier()
            assert notifier.webhooks[DiscordChannel.TRADES] == "https://main.webhook"
            assert notifier.webhooks[DiscordChannel.RISK] == "https://main.webhook"

    def test_channel_specific_webhooks(self):
        """When channel-specific webhooks are set, they should be used."""
        env = {
            "DISCORD_WEBHOOK_URL": "https://main.webhook",
            "DISCORD_WEBHOOK_TRADES": "https://trades.webhook",
            "DISCORD_WEBHOOK_RISK": "https://risk.webhook",
        }
        with patch.dict("os.environ", env, clear=True):
            notifier = DiscordNotifier()
            assert notifier.webhooks[DiscordChannel.TRADES] == "https://trades.webhook"
            assert notifier.webhooks[DiscordChannel.RISK] == "https://risk.webhook"
            # Health should fallback to main
            assert notifier.webhooks[DiscordChannel.HEALTH] == "https://main.webhook"


class TestSendMessage:
    """Tests for send_message method."""

    def test_send_message(self, notifier, mock_requests_post):
        notifier.send_message("Hello World")
        
        mock_requests_post.assert_called_once()
        args, kwargs = mock_requests_post.call_args
        assert kwargs['json']['content'] == "Hello World"
        assert kwargs['json']['username'] == "Forex Agent"

    def test_send_message_disabled(self, mock_requests_post):
        with patch.dict("os.environ", {}, clear=True):
            notifier = DiscordNotifier()
            notifier.send_message("Hello World")
            mock_requests_post.assert_not_called()


class TestTradeAlerts:
    """Tests for trade-related alerts."""

    def test_send_trade_alert_filled(self, notifier, mock_requests_post):
        signal = {
            'direction': 'LONG',
            'symbol': 'EURUSD',
            'entry_price': 1.0500,
            'stop_loss': 1.0450,
            'take_profit': 1.0600,
            'rationale': 'Test Rationale',
            'timestamp': MagicMock(isoformat=MagicMock(return_value="2026-01-26T12:00:00"))
        }
        order_intent = MagicMock()
        order_intent.quantity = 1000
        
        result = MagicMock()
        result.status = "FILLED"
        result.order_id = "ORDER-123"
        
        notifier.send_trade_alert(signal, order_intent, result)
        
        mock_requests_post.assert_called_once()
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        
        assert "FILLED" in embed['title']
        assert "LONG EURUSD" in embed['title']
        assert embed['color'] == 5763719  # Green

    def test_send_trade_alert_rejected(self, notifier, mock_requests_post):
        signal = {
            'direction': 'SHORT',
            'symbol': 'GBPUSD',
            'timestamp': MagicMock(isoformat=MagicMock(return_value="2026-01-26T12:00:00"))
        }
        order_intent = MagicMock(quantity=500)
        result = MagicMock(status="REJECTED", order_id="ORDER-456")
        
        notifier.send_trade_alert(signal, order_intent, result)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "REJECTED" in embed['title']
        assert embed['color'] == 15548997  # Red

    def test_send_close_alert_profit(self, notifier, mock_requests_post):
        trade = {
            'direction': 'LONG',
            'symbol': 'USDJPY',
            'entry_price': 150.00,
            'exit_price': 151.00,
            'quantity': 10000,
            'broker_order_id': 'ORDER-456'
        }
        
        notifier.send_close_alert(trade, pnl=100.0)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "CLOSED: LONG USDJPY" in embed['title']
        assert embed['color'] == 5763719  # Green
        
        fields = {f['name']: f['value'] for f in embed['fields']}
        assert fields['💵 PnL'] == "+100.00"

    def test_send_close_alert_loss(self, notifier, mock_requests_post):
        trade = {'direction': 'SHORT', 'symbol': 'EURUSD'}
        notifier.send_close_alert(trade, pnl=-50.0)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert embed['color'] == 15548997  # Red
        
        fields = {f['name']: f['value'] for f in embed['fields']}
        assert fields['💵 PnL'] == "-50.00"


class TestErrorAlerts:
    """Tests for error alerts."""

    def test_send_error(self, notifier, mock_requests_post):
        notifier.send_error("Something broke")
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "CRITICAL ERROR" in embed['title']
        assert embed['description'] == "Something broke"
        assert embed['color'] == 15548997  # Red


class TestRiskAlerts:
    """Tests for risk-related alerts."""

    def test_send_risk_alert(self, notifier, mock_requests_post):
        details = {
            'current': '2.5%',
            'limit': '2.0%',
            'action': 'Trading PAUSED until reset'
        }
        
        notifier.send_risk_alert("DAILY_LOSS_LIMIT", details)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "RISK LIMIT HIT" in embed['title']
        assert embed['color'] == 16744256  # Orange
        
        fields = {f['name']: f['value'] for f in embed['fields']}
        assert fields['⚠️ Type'] == "DAILY_LOSS_LIMIT"
        assert fields['📊 Current'] == "2.5%"
        assert fields['🛑 Limit'] == "2.0%"


class TestHealthStatus:
    """Tests for health status updates."""

    def test_send_health_status_ok(self, notifier, mock_requests_post):
        details = {
            'broker': 'IG-DEMO connected',
            'data_feed': 'TwelveData OK',
            'last_candle': '16:55 UTC',
            'db': 'trades.db (45 records)',
            'uptime': '4h 32m'
        }
        
        notifier.send_health_status("OK", details)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "SYSTEM HEALTH — OK" in embed['title']
        assert embed['color'] == 5763719  # Green

    def test_send_health_status_degraded(self, notifier, mock_requests_post):
        details = {'broker': 'Connected', 'data_feed': 'Delayed'}
        
        notifier.send_health_status("DEGRADED", details)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "DEGRADED" in embed['title']
        assert embed['color'] == 16744256  # Orange

    def test_send_health_status_down(self, notifier, mock_requests_post):
        details = {'broker': 'Disconnected', 'data_feed': 'Down'}
        
        notifier.send_health_status("DOWN", details)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "DOWN" in embed['title']
        assert embed['color'] == 15548997  # Red


class TestReports:
    """Tests for report notifications."""

    def test_send_daily_summary_profit(self, notifier, mock_requests_post):
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
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "DAILY REPORT" in embed['title']
        assert "2026-01-25" in embed['title']
        assert embed['color'] == 5763719  # Green (profit)
        
        fields = {f['name']: f['value'] for f in embed['fields']}
        assert fields['📊 Trades'] == "5"
        assert fields['✅ Wins'] == "3"
        assert "+150.00" in fields['📈 PnL']

    def test_send_daily_summary_loss(self, notifier, mock_requests_post):
        summary = {
            'date': '2026-01-25',
            'total_trades': 3,
            'wins': 1,
            'losses': 2,
            'total_pnl': -75.0,
            'equity': 9925.0,
            'win_rate': 33.3
        }
        
        notifier.send_daily_summary(summary)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert embed['color'] == 15548997  # Red (loss)
        
        fields = {f['name']: f['value'] for f in embed['fields']}
        assert "-75.00" in fields['📉 PnL']

    def test_send_weekly_summary(self, notifier, mock_requests_post):
        summary = {
            'week': 'W04 2026',
            'total_trades': 25,
            'total_pnl': 500.0,
            'win_rate': 68.0,
            'max_drawdown': 3.2,
            'risk_events': 1,
            'errors_count': 0
        }
        
        notifier.send_weekly_summary(summary)
        
        embed = mock_requests_post.call_args[1]['json']['embeds'][0]
        assert "WEEKLY REPORT" in embed['title']
        assert "W04 2026" in embed['title']
        
        fields = {f['name']: f['value'] for f in embed['fields']}
        assert fields['📊 Total Trades'] == "25"
        assert fields['📉 Max Drawdown'] == "3.20%"


class TestChannelRouting:
    """Tests for channel-specific webhook routing."""

    def test_trade_alerts_use_trades_channel(self, mock_requests_post):
        env = {
            "DISCORD_WEBHOOK_URL": "https://main.webhook",
            "DISCORD_WEBHOOK_TRADES": "https://trades.webhook",
        }
        with patch.dict("os.environ", env, clear=True):
            notifier = DiscordNotifier()
            trade = {'direction': 'LONG', 'symbol': 'EURUSD'}
            notifier.send_close_alert(trade, pnl=50.0)
            
            # Should use trades webhook
            call_url = mock_requests_post.call_args[0][0]
            assert call_url == "https://trades.webhook"

    def test_risk_alerts_use_risk_channel(self, mock_requests_post):
        env = {
            "DISCORD_WEBHOOK_URL": "https://main.webhook",
            "DISCORD_WEBHOOK_RISK": "https://risk.webhook",
        }
        with patch.dict("os.environ", env, clear=True):
            notifier = DiscordNotifier()
            notifier.send_risk_alert("TEST_ALERT", {'current': '1', 'limit': '2'})
            
            call_url = mock_requests_post.call_args[0][0]
            assert call_url == "https://risk.webhook"

    def test_health_status_uses_health_channel(self, mock_requests_post):
        env = {
            "DISCORD_WEBHOOK_URL": "https://main.webhook",
            "DISCORD_WEBHOOK_HEALTH": "https://health.webhook",
        }
        with patch.dict("os.environ", env, clear=True):
            notifier = DiscordNotifier()
            notifier.send_health_status("OK", {'broker': 'Connected'})
            
            call_url = mock_requests_post.call_args[0][0]
            assert call_url == "https://health.webhook"

    def test_reports_use_reports_channel(self, mock_requests_post):
        env = {
            "DISCORD_WEBHOOK_URL": "https://main.webhook",
            "DISCORD_WEBHOOK_REPORTS": "https://reports.webhook",
        }
        with patch.dict("os.environ", env, clear=True):
            notifier = DiscordNotifier()
            notifier.send_daily_summary({'date': '2026-01-25', 'total_pnl': 100})
            
            call_url = mock_requests_post.call_args[0][0]
            assert call_url == "https://reports.webhook"


class TestErrorHandling:
    """Tests for error handling."""

    def test_timeout_handling(self, notifier):
        import requests
        with patch("execution.notifier.requests.post") as mock_post:
            mock_post.side_effect = requests.Timeout()
            
            # Should not raise, just log warning
            notifier.send_message("Test")

    def test_request_exception_handling(self, notifier):
        import requests
        with patch("execution.notifier.requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("Connection failed")
            
            # Should not raise, just log error
            notifier.send_message("Test")
