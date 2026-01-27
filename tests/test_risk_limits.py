import pytest
from unittest.mock import patch, MagicMock
from execution.risk_limits import RiskConfig, RiskManager, check_daily_limits, check_exposure_limits


@pytest.fixture
def risk_config():
    """Standard risk configuration for testing."""
    return RiskConfig(
        max_daily_loss_pct=2.0,
        max_trades_per_day=5,
        max_open_lots=1.0
    )


@pytest.fixture
def mock_notifier():
    """Mock Discord notifier."""
    notifier = MagicMock()
    notifier.send_risk_alert = MagicMock()
    return notifier


class TestRiskConfig:
    """Tests for RiskConfig dataclass."""

    def test_default_values(self):
        config = RiskConfig()
        assert config.max_daily_loss_pct == 2.0
        assert config.max_trades_per_day == 5
        assert config.risk_per_trade_pct == 1.0
        assert config.max_open_lots == 1.0

    def test_custom_values(self):
        config = RiskConfig(max_daily_loss_pct=3.0, max_trades_per_day=10)
        assert config.max_daily_loss_pct == 3.0
        assert config.max_trades_per_day == 10


class TestRiskManager:
    """Tests for RiskManager class."""

    def test_daily_limits_ok(self, risk_config, mock_notifier):
        manager = RiskManager(config=risk_config, notifier=mock_notifier)
        
        account = {
            "daily_loss_current": 10.0,
            "equity": 10000.0,
            "daily_trades_count": 2
        }
        
        result = manager.check_daily_limits(account)
        
        assert result["allowed"] is True
        assert result["reason"] == "OK"
        assert result["alert_sent"] is False
        mock_notifier.send_risk_alert.assert_not_called()

    def test_daily_loss_limit_hit(self, risk_config, mock_notifier):
        manager = RiskManager(config=risk_config, notifier=mock_notifier)
        
        account = {
            "daily_loss_current": 250.0,  # 2.5% of 10000
            "equity": 10000.0,
            "daily_trades_count": 2
        }
        
        result = manager.check_daily_limits(account)
        
        assert result["allowed"] is False
        assert "DAILY_LOSS_LIMIT" in result["reason"]
        assert result["alert_sent"] is True
        mock_notifier.send_risk_alert.assert_called_once()
        
        call_args = mock_notifier.send_risk_alert.call_args
        assert call_args[0][0] == "DAILY_LOSS_LIMIT"
        assert "2.50%" in call_args[0][1]["current"]

    def test_max_trades_limit_hit(self, risk_config, mock_notifier):
        manager = RiskManager(config=risk_config, notifier=mock_notifier)
        
        account = {
            "daily_loss_current": 0.0,
            "equity": 10000.0,
            "daily_trades_count": 5  # At limit
        }
        
        result = manager.check_daily_limits(account)
        
        assert result["allowed"] is False
        assert "MAX_TRADES_LIMIT" in result["reason"]
        mock_notifier.send_risk_alert.assert_called_once()

    def test_equity_zero(self, risk_config, mock_notifier):
        manager = RiskManager(config=risk_config, notifier=mock_notifier)
        
        account = {"equity": 0}
        
        result = manager.check_daily_limits(account)
        
        assert result["allowed"] is False
        assert "EQUITY_ZERO_OR_NEGATIVE" in result["reason"]

    def test_exposure_limit_ok(self, risk_config, mock_notifier):
        manager = RiskManager(config=risk_config, notifier=mock_notifier)
        
        account = {
            "open_positions": [
                {"size": 0.3},
                {"size": 0.2}
            ]
        }
        
        result = manager.check_exposure_limits(account, new_size_lots=0.4)
        
        assert result["allowed"] is True
        mock_notifier.send_risk_alert.assert_not_called()

    def test_exposure_limit_exceeded(self, risk_config, mock_notifier):
        manager = RiskManager(config=risk_config, notifier=mock_notifier)
        
        account = {
            "open_positions": [
                {"size": 0.5},
                {"size": 0.3}
            ]
        }
        
        result = manager.check_exposure_limits(account, new_size_lots=0.5)
        
        assert result["allowed"] is False
        assert "MAX_EXPOSURE_LIMIT" in result["reason"]
        mock_notifier.send_risk_alert.assert_called_once()


class TestLegacyFunctions:
    """Tests for backward-compatible legacy functions."""

    def test_check_daily_limits_legacy(self, risk_config):
        account = {
            "daily_loss_current": 10.0,
            "equity": 10000.0,
            "daily_trades_count": 2
        }
        
        result = check_daily_limits(account, risk_config)
        
        assert result["allowed"] is True
        assert result["reason"] == "OK"
        # Legacy function should not have alert_sent key
        assert "alert_sent" not in result or result.get("alert_sent") is None

    def test_check_exposure_limits_legacy(self, risk_config):
        account = {"open_positions": []}
        
        result = check_exposure_limits(account, 0.5, risk_config)
        
        assert result["allowed"] is True


class TestAlertNotSentOnSuccess:
    """Verify alerts are only sent on failures."""

    def test_no_alert_when_within_limits(self, risk_config, mock_notifier):
        manager = RiskManager(config=risk_config, notifier=mock_notifier)
        
        # All checks pass
        account = {
            "daily_loss_current": 50.0,  # 0.5% - well within 2% limit
            "equity": 10000.0,
            "daily_trades_count": 1,
            "open_positions": [{"size": 0.2}]
        }
        
        manager.check_daily_limits(account)
        manager.check_exposure_limits(account, 0.3)
        
        # No alerts should have been sent
        mock_notifier.send_risk_alert.assert_not_called()
