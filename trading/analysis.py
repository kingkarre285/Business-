"""Scanner und Backtest für die Regel "mindestens X % netto pro Trade".

Scanner: Wie oft hat sich der Kurs innerhalb des Zeitfensters überhaupt weit
genug bewegt? Unterstellt PERFEKTE Vorhersage der Richtung, also eine Obergrenze,
die keine echte Strategie erreicht.

Backtest: Eine Einstiegsregel (Breakout, Trendfolge oder Rücksetzer) handelt
mit festem Ziel (X % netto) und Stop-Loss. Ergebnis zeigt, was nach Kosten
tatsächlich übrig bleibt.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import config as cfg


def _ts(c: dict) -> datetime:
    return datetime.fromisoformat(c["time"].replace("Z", "+00:00"))


def _sma(values: list[float], n: int) -> list[float | None]:
    out, total = [], 0.0
    for i, v in enumerate(values):
        total += v
        if i >= n:
            total -= values[i - n]
        out.append(total / n if i >= n - 1 else None)
    return out


def _rsi(closes: list[float], n: int = 14) -> list[float | None]:
    """RSI nach Wilder."""
    out: list[float | None] = [None] * len(closes)
    if len(closes) <= n:
        return out
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    avg_g, avg_l = sum(gains[:n]) / n, sum(losses[:n]) / n
    for i in range(n, len(closes)):
        if i > n:
            avg_g = (avg_g * (n - 1) + gains[i - 1]) / n
            avg_l = (avg_l * (n - 1) + losses[i - 1]) / n
        out[i] = 100.0 if avg_l == 0 else 100 - 100 / (1 + avg_g / avg_l)
    return out


STRATEGIES = {
    "breakout": "Breakout über das Hoch / unter das Tief des Zeitfensters davor",
    "trend": "Trendfolge: Long, wenn Kurs > 50-Perioden-Schnitt > 200-Perioden-Schnitt; "
             "Short umgekehrt",
    "pullback": "Rücksetzer: Long bei RSI(14) < 30 über dem 200-Perioden-Schnitt; "
                "Short bei RSI(14) > 70 darunter",
}


def _signals(candles: list[dict], strategy: str):
    """Liefert (erster nutzbarer Index, Funktion i -> +1 / -1 / 0)."""
    closes = [c["close"] for c in candles]
    if strategy == "breakout":
        n = max(1, cfg.BREAKOUT_LOOKBACK_HOURS // cfg.INTERVAL_HOURS[cfg.CANDLE_INTERVAL])

        def signal(i: int) -> int:
            prev = candles[i - n:i]
            if closes[i] > max(c["high"] for c in prev):
                return 1
            if closes[i] < min(c["low"] for c in prev):
                return -1
            return 0
        return n, signal

    sma50, sma200 = _sma(closes, 50), _sma(closes, 200)
    if strategy == "trend":
        def signal(i: int) -> int:
            if closes[i] > sma50[i] > sma200[i]:
                return 1
            if closes[i] < sma50[i] < sma200[i]:
                return -1
            return 0
        return 199, signal

    if strategy == "pullback":
        rsi = _rsi(closes)

        def signal(i: int) -> int:
            if closes[i] > sma200[i] and rsi[i] < 30:
                return 1
            if closes[i] < sma200[i] and rsi[i] > 70:
                return -1
            return 0
        return 199, signal

    raise ValueError(f"unbekannte Strategie: {strategy}")


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
    risk: float = 0.0  # geplanter Verlust bis zum ersten Stop, bezogen auf den Einsatz


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


def _atr(candles: list[dict], n: int = 14) -> list[float | None]:
    """Average True Range nach Wilder."""
    out: list[float | None] = [None] * len(candles)
    trs = [candles[0]["high"] - candles[0]["low"]] + [
        max(c["high"], p["close"]) - min(c["low"], p["close"])
        for p, c in zip(candles, candles[1:])
    ]
    if len(trs) < n:
        return out
    atr = sum(trs[:n]) / n
    out[n - 1] = atr
    for i in range(n, len(trs)):
        atr = (atr * (n - 1) + trs[i]) / n
        out[i] = atr
    return out


def backtest(symbol: str, candles: list[dict], strategy: str = "breakout") -> BacktestResult:
    if getattr(cfg, "EXIT_MODE", "fixed") == "trailing":
        return backtest_trailing(symbol, candles, strategy)
    lev = cfg.leverage_for(symbol)
    cost = cfg.cost_for(symbol) / 100
    target_move = cfg.required_move_pct(symbol) / 100
    stop_move = cfg.stop_move_pct(symbol) / 100
    overnight = cfg.overnight_for(symbol) / 100
    first, signal = _signals(candles, strategy)

    res = BacktestResult(symbol)
    if stop_move <= 0:
        return res  # Kosten allein sind höher als der erlaubte Verlust
    equity = cfg.START_CAPITAL
    i = first
    while i < len(candles) - 1 and equity >= cfg.START_CAPITAL * 0.01:
        d = signal(i)
        if d == 0:
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
                                outcome, r, cfg.STOP_LOSS_PCT_OF_MARGIN / 100))
        res.equity_curve.append(equity)
        i = j + 1
    return res


def backtest_trailing(symbol: str, candles: list[dict], strategy: str) -> BacktestResult:
    """Ohne festes Kursziel: Der Stop startet ATR_MULT × ATR vom Einstieg entfernt
    und wird mit dem besten Kurs seit Einstieg nachgezogen (nie zurück).
    Spätestens nach HORIZON_HOURS wird geschlossen."""
    lev = cfg.leverage_for(symbol)
    cost = cfg.cost_for(symbol) / 100
    overnight = cfg.overnight_for(symbol) / 100
    first, signal = _signals(candles, strategy)
    atr = _atr(candles)

    res = BacktestResult(symbol)
    equity = cfg.START_CAPITAL
    i = max(first, 14)
    while i < len(candles) - 1:
        d = signal(i)
        if d == 0 or atr[i] is None:
            i += 1
            continue
        entry = candles[i + 1]["open"]
        dist = cfg.ATR_MULT * atr[i]
        stop = entry - d * dist
        best = entry
        end = _window_end(candles, i + 1)
        exit_price, outcome, j = candles[end - 1]["close"], "Zeit", end - 1
        for j in range(i + 1, end):
            c = candles[j]
            if (d == 1 and c["low"] <= stop) or (d == -1 and c["high"] >= stop):
                gap = (d == 1 and c["open"] < stop) or (d == -1 and c["open"] > stop)
                exit_price, outcome = (c["open"] if gap else stop), "Stop"
                break
            # Stop erst nach Ende der Kerze nachziehen (kein Blick in die Zukunft).
            best = max(best, c["high"]) if d == 1 else min(best, c["low"])
            stop = max(stop, best - dist) if d == 1 else min(stop, best + dist)

        nights = (_ts(candles[j]).date() - _ts(candles[i + 1]).date()).days
        r = max(lev * (d * (exit_price / entry - 1) - cost - overnight * nights), -1.0)
        risk = lev * (dist / entry + cost)
        equity *= 1 + 0.01 * r / risk  # 1 % Risiko pro Trade, nur für die Einzelauswertung
        res.trades.append(Trade(candles[i + 1]["time"], candles[j]["time"], d, entry,
                                exit_price, outcome, r, risk))
        res.equity_curve.append(equity)
        i = j + 1
    return res


def period_multipliers(result: BacktestResult, candles: list[dict], days: int = 7) -> list[float]:
    """Faktor, um den sich das Konto in jedem Zeitraum (Blöcke von `days` Tagen
    ab Beginn der Kursdaten) verändert hat. 2.0 = verdoppelt."""
    start, end = _ts(candles[0]), _ts(candles[-1])
    points = [(datetime.fromisoformat(t.exit_time.replace("Z", "+00:00")), e)
              for t, e in zip(result.trades, result.equity_curve)]
    factors = []
    week_start, equity_at_start = start, cfg.START_CAPITAL
    while week_start + timedelta(days=days) <= end:
        week_end = week_start + timedelta(days=days)
        equity_at_end = equity_at_start
        for t, e in points:
            if week_start <= t < week_end:
                equity_at_end = e
        if equity_at_start > 0:
            factors.append(equity_at_end / equity_at_start)
        week_start, equity_at_start = week_end, equity_at_end
    return factors
