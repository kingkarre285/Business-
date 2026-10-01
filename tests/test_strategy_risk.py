import numpy as np
import pandas as pd

from etoro_bot import risk
from etoro_bot.brokers import PaperBroker
from etoro_bot.strategy import generate_signal

CFG = {"fast_sma": 20, "slow_sma": 50, "trend_sma": 200, "rsi_period": 14, "rsi_max_entry": 70,
       "rsi_min_short": 30, "atr_period": 14, "stop_atr_mult": 2.0, "take_profit_atr_mult": 4.0}
RISK = {"risk_per_trade_pct": 1.0, "max_position_pct": 15.0, "max_exposure_pct": 30.0,
        "min_order_usd": 50, "max_daily_loss_pct": 3.0, "leverage": 2}


def frame(close):
    close = pd.Series(close, dtype=float)
    return pd.DataFrame({"open": close, "high": close * 1.01, "low": close * 0.99, "close": close})


def noisy(start, end, n=300, seed=1):
    return np.linspace(start, end, n) + np.random.default_rng(seed).normal(0, abs(end - start) / 60, n)


def test_downtrend_never_buys_and_shorts_only_when_allowed():
    df = frame(noisy(200, 100))
    assert generate_signal(df, CFG, None).action in ("hold",)
    sig = generate_signal(df, {**CFG, "allow_short": True}, None)
    assert sig.action in ("short", "hold")
    if sig.action == "short":
        assert sig.take_profit < sig.price < sig.stop_loss


def test_uptrend_buy_has_stop_below_target_above():
    sig = generate_signal(frame(noisy(100, 160)), {**CFG, "allow_short": True}, None)
    assert sig.action != "short"
    if sig.action == "buy":
        assert sig.stop_loss < sig.price < sig.take_profit


def test_trend_reversal_closes_long_and_short():
    up_then_down = frame(np.concatenate([np.linspace(100, 200, 250), np.linspace(200, 150, 50)]))
    assert generate_signal(up_then_down, CFG, "long").action == "close"
    down_then_up = frame(np.concatenate([np.linspace(200, 100, 250), np.linspace(100, 150, 50)]))
    assert generate_signal(down_then_up, CFG, "short").action == "close"


def test_position_size_risk_independent_of_leverage():
    # 1 % Risiko bei 5 % Stop-Abstand -> 2000 USD Exposure
    # ohne Hebel begrenzt der max. Einsatz (15 %) die Größe
    assert risk.position_size(10000, 100, 95, RISK, leverage=1) == (1500, 1500)
    assert risk.position_size(10000, 100, 95, RISK, leverage=2) == (2000, 1000)
    # Short: Stop über dem Kurs
    assert risk.position_size(10000, 100, 105, RISK, leverage=2) == (2000, 1000)
    # Enger Stop -> gedeckelt auf 30 % Exposure
    assert risk.position_size(10000, 100, 99.5, RISK, leverage=5) == (3000, 600)
    # Index-Mindest-Exposure 1000 USD
    assert risk.position_size(3000, 100, 95, RISK, leverage=2, min_exposure=1000) == (0, 0)


def test_daily_loss_stop():
    assert risk.daily_loss_exceeded(10000, 9650, RISK)
    assert not risk.daily_loss_exceeded(10000, 9800, RISK)


def test_paper_long_stop_loss(tmp_path):
    b = PaperBroker(tmp_path / "s.json", 10000)
    b.open({"symbol": "X"}, "long", 2000, 1000, 2, 100, 90, 120, print)
    b.check_stops("X", low=89, high=101, log=print)
    assert "X" not in b.positions([])
    assert round(b.state["cash"], 2) == 9800  # 10 % von 2000 Exposure verloren


def test_paper_short_take_profit(tmp_path):
    b = PaperBroker(tmp_path / "s.json", 10000)
    b.open({"symbol": "X"}, "short", 2000, 1000, 2, 100, 110, 80, print)
    b.update_price("X", 90)
    assert round(b.equity(), 2) == 10200
    b.check_stops("X", low=79, high=95, log=print)
    assert round(b.state["cash"], 2) == 10400  # 20 % Kursrückgang auf 2000 Exposure
