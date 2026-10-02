"""Scanner und Backtest für die Regel "mindestens X % netto pro Trade".

Scanner: Wie oft hat sich der Kurs innerhalb des Zeitfensters überhaupt weit
genug bewegt? Unterstellt PERFEKTE Vorhersage der Richtung, also eine Obergrenze,
die keine echte Strategie erreicht.

Backtest: Eine einfache Breakout-Strategie handelt mit festem Ziel (X % netto)
und Stop-Loss. Ergebnis zeigt, was nach Kosten tatsächlich übrig bleibt.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import config as cfg


def _ts(c: dict) -> datetime:
    return datetime.fromisoformat(c["time"].replace("Z", "+00:00"))


def _window_end(candles: list[dict], start: int) -> int:
    """Index (exklusiv) der letzten Kerze innerhalb von HORIZON_HOURS nach start."""
    limit = _ts(candles[start]) + timedelta(hours=cfg.HORIZON_HOURS)
    j = start + 1
    while j < len(candles) and _ts(candles[j]) < limit:
        j += 1
    return j


def scan(symbol: str, candles: list[dict]) -> dict:
    """Anteil der Zeitpunkte, ab denen die nötige Bewegung (in irgendeine
    Richtung) innerhalb des Zeitfensters erreicht wurde."""
    need = cfg.required_move_pct(symbol) / 100
    horizon_end = _ts(candles[-1]) - timedelta(hours=cfg.HORIZON_HOURS)
    hits = total = 0
    for i, c in enumerate(candles):
        if _ts(c) > horizon_end:
            break
        end = _window_end(candles, i)
        window = candles[i + 1:end]
        if not window:
            continue
        entry = c["close"]
        up = max(w["high"] for w in window) / entry - 1
        down = 1 - min(w["low"] for w in window) / entry
        total += 1
        hits += up >= need or down >= need
    return {"windows": total, "hits": hits, "hit_rate": hits / total if total else 0.0}


@dataclass
class Trade:
    entry_time: str
    exit_time: str
    direction: int  # +1 long, -1 short
    entry: float
    exit: float
    outcome: str  # "Ziel", "Stop", "Zeit"
    net_return: float  # bezogen auf den Einsatz, 0.57 = +57 %


@dataclass
class BacktestResult:
    symbol: str
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[float] = field(default_factory=list)

    @property
    def final_equity(self) -> float:
        return self.equity_curve[-1] if self.equity_curve else cfg.START_CAPITAL

    @property
    def wins(self) -> int:
        return sum(t.outcome == "Ziel" for t in self.trades)

    @property
    def max_drawdown(self) -> float:
        peak, mdd = cfg.START_CAPITAL, 0.0
        for e in self.equity_curve:
            peak = max(peak, e)
            mdd = max(mdd, 1 - e / peak)
        return mdd

    @property
    def ruined(self) -> bool:
        return self.final_equity < cfg.START_CAPITAL * 0.01


def backtest(symbol: str, candles: list[dict]) -> BacktestResult:
    lev = cfg.leverage_for(symbol)
    cost = cfg.cost_for(symbol) / 100
    target_move = cfg.required_move_pct(symbol) / 100
    stop_move = cfg.stop_move_pct(symbol) / 100
    overnight = cfg.overnight_for(symbol) / 100
    n = max(1, cfg.BREAKOUT_LOOKBACK_HOURS // cfg.INTERVAL_HOURS[cfg.CANDLE_INTERVAL])

    res = BacktestResult(symbol)
    if stop_move <= 0:
        return res  # Kosten allein sind höher als der erlaubte Verlust
    equity = cfg.START_CAPITAL
    i = n
    while i < len(candles) - 1 and equity >= cfg.START_CAPITAL * 0.01:
        prev = candles[i - n:i]
        close = candles[i]["close"]
        if close > max(c["high"] for c in prev):
            d = 1
        elif close < min(c["low"] for c in prev):
            d = -1
        else:
            i += 1
            continue

        entry = candles[i + 1]["open"]
        target = entry * (1 + d * target_move)
        stop = entry * (1 - d * stop_move)
        end = _window_end(candles, i + 1)
        exit_price, outcome, j = candles[end - 1]["close"], "Zeit", end - 1
        for j in range(i + 1, end):
            c = candles[j]
            # Stop zuerst prüfen (konservativ); bei Kurslücke zum Eröffnungskurs.
            if (d == 1 and c["low"] <= stop) or (d == -1 and c["high"] >= stop):
                gap = (d == 1 and c["open"] < stop) or (d == -1 and c["open"] > stop)
                exit_price, outcome = (c["open"] if gap else stop), "Stop"
                break
            if (d == 1 and c["high"] >= target) or (d == -1 and c["low"] <= target):
                exit_price, outcome = target, "Ziel"
                break

        # Übernachtgebühr für jede angefangene Nacht, in der die Position offen war.
        exit_time = candles[j]["time"]
        nights = (_ts(candles[j]).date() - _ts(candles[i + 1]).date()).days
        r = lev * (d * (exit_price / entry - 1) - cost - overnight * nights)
        r = max(r, -1.0)  # mehr als der Einsatz kann nicht verloren gehen
        stake = equity * cfg.STAKE_PCT_OF_EQUITY / 100
        equity += stake * r
        res.trades.append(Trade(candles[i + 1]["time"], exit_time, d, entry, exit_price,
                                outcome, r))
        res.equity_curve.append(equity)
        i = j + 1
    return res


def weekly_multipliers(result: BacktestResult, candles: list[dict]) -> list[float]:
    """Faktor, um den sich das Konto in jeder Kalenderwoche (7-Tage-Blöcke ab
    Beginn der Kursdaten) verändert hat. 2.0 = verdoppelt."""
    start, end = _ts(candles[0]), _ts(candles[-1])
    points = [(datetime.fromisoformat(t.exit_time.replace("Z", "+00:00")), e)
              for t, e in zip(result.trades, result.equity_curve)]
    factors = []
    week_start, equity_at_start = start, cfg.START_CAPITAL
    while week_start + timedelta(days=7) <= end:
        week_end = week_start + timedelta(days=7)
        equity_at_end = equity_at_start
        for t, e in points:
            if week_start <= t < week_end:
                equity_at_end = e
        if equity_at_start > 0:
            factors.append(equity_at_end / equity_at_start)
        week_start, equity_at_start = week_end, equity_at_end
    return factors
