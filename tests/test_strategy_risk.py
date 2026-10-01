import numpy as np
import pandas as pd

from etoro_bot import risk
from etoro_bot.brokers import PaperBroker
from etoro_bot.strategy import generate_signal

CFG = {"fast_sma": 20, "slow_sma": 50, "trend_sma": 200, "rsi_period": 14, "rsi_max_entry": 70,
       "atr_period": 14, "stop_atr_mult": 2.0, "take_profit_atr_mult": 4.0}
RISK = {"risk_per_trade_pct": 1.0, "max_position_pct": 15.0, "min_order_usd": 50, "max_daily_loss_pct": 3.0}


def frame(close):
    close = pd.Series(close, dtype=float)
    return pd.DataFrame({"open": close, "high": close * 1.01, "low": close * 0.99, "close": close})


def test_downtrend_never_buys():
    df = frame(np.linspace(200, 100, 300))
    assert generate_signal(df, CFG, has_position=False).action == "hold"


def test_trend_break_sells_open_position():
    df = frame(np.concatenate([np.linspace(100, 200, 250), np.linspace(200, 150, 50)]))
    assert generate_signal(df, CFG, has_position=True).action == "sell"


def test_buy_signal_has_stop_below_and_target_above_price():
    rng = np.random.default_rng(1)
    df = frame(np.linspace(100, 160, 300) + rng.normal(0, 1.5, 300))
    sig = generate_signal(df, CFG, has_position=False)
    if sig.action == "buy":
        assert sig.stop_loss < sig.price < sig.take_profit


def test_position_size_respects_risk_and_cap():
    # 1 % Risiko bei 10 % Stop-Abstand -> 1000 USD, Cap 15 % -> 1500
    assert risk.position_size_usd(10000, 100, 90, RISK) == 1000
    assert risk.position_size_usd(10000, 100, 99, RISK) == 1500
    assert risk.position_size_usd(1000, 100, 50, RISK) == 0  # unter Mindestbetrag
    assert risk.position_size_usd(10000, 100, 101, RISK) == 0  # ungültiger Stop
    assert risk.position_size_usd(10000, 100, 90, RISK, min_usd=1000) == 1000
    assert risk.position_size_usd(5000, 100, 90, RISK, min_usd=1000) == 0  # Index-Minimum


def test_daily_loss_stop():
    assert risk.daily_loss_exceeded(10000, 9650, RISK)
    assert not risk.daily_loss_exceeded(10000, 9800, RISK)


def test_paper_stop_loss_triggers(tmp_path):
    b = PaperBroker(tmp_path / "s.json", 10000)
    b.open_long({"symbol": "X"}, 1000, 100, 90, 120, print)
    b.check_stops("X", low=89, high=101, log=print)
    assert "X" not in b.positions()
    assert round(b.state["cash"], 2) == 9900
