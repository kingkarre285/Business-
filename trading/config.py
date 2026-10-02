"""Einstellungen für Scanner und Backtest.

Alle Kosten sind SCHÄTZUNGEN für eToro (Spread bzw. Gebühr pro Hin- und Rückweg
in Prozent des Positionswerts). Vor echtem Einsatz mit den aktuellen Werten in
der eToro-App abgleichen.
"""

# Mindest-Nettogewinn pro Trade, bezogen auf den eingesetzten Betrag (Margin),
# nach Abzug der Kosten. 57.0 = +57 %.
MIN_NET_PROFIT_PCT = 57.0

# Zeitfenster, in dem das Ziel erreicht sein muss (in Stunden).
HORIZON_HOURS = 24

# Stop-Loss bezogen auf den Einsatz: 50.0 = Trade wird bei -50 % des Einsatzes
# geschlossen. 100.0 = kein Stop, Totalverlust des Einsatzes möglich.
STOP_LOSS_PCT_OF_MARGIN = 50.0

# Anteil des Kontos, der pro Trade eingesetzt wird (100 = alles, wie im Video).
STAKE_PCT_OF_EQUITY = 100.0

START_CAPITAL = 100.0

# Maximaler Hebel für Privatkunden (ESMA-Grenzen, wie bei eToro EU)
# und geschätzte Kosten pro Round-Trip in % des Positionswerts.
ASSET_CLASSES = {
    "Crypto":    {"max_leverage": 2,  "cost_pct": 2.00},  # 1 % Gebühr je Kauf/Verkauf
    "Stocks":    {"max_leverage": 5,  "cost_pct": 0.30},
    "Forex":     {"max_leverage": 30, "cost_pct": 0.02},
    "Commodity": {"max_leverage": 10, "cost_pct": 0.10},
    "Indices":   {"max_leverage": 20, "cost_pct": 0.05},
}

# Forex-Majors dürfen 30x, Nebenwerte/Kreuzkurse nur 20x.
LEVERAGE_OVERRIDES = {"GBPJPY": 20, "GOLD": 20}

# Instrumente (Symbol -> (eToro instrumentId, Anlageklasse)).
UNIVERSE = {
    "BTC":     (100000, "Crypto"),
    "ETH":     (100001, "Crypto"),
    "SOL":     (100063, "Crypto"),
    "XRP":     (100003, "Crypto"),
    "DOGE":    (100043, "Crypto"),
    "TSLA":    (1111,   "Stocks"),
    "NVDA":    (1137,   "Stocks"),
    "AMD":     (1832,   "Stocks"),
    "COIN":    (6168,   "Stocks"),
    "MSTR":    (6473,   "Stocks"),
    "PLTR":    (7991,   "Stocks"),
    "EURUSD":  (1,      "Forex"),
    "USDJPY":  (5,      "Forex"),
    "GBPJPY":  (11,     "Forex"),
    "GOLD":    (18,     "Commodity"),
    "SILVER":  (19,     "Commodity"),
    "OIL":     (17,     "Commodity"),
    "SPX500":  (27,     "Indices"),
    "NSDQ100": (28,     "Indices"),
    "GER40":   (32,     "Indices"),
}

# Breakout-Signal: Long, wenn der Schlusskurs über dem Hoch der letzten N Stunden
# liegt, Short, wenn er darunter liegt.
BREAKOUT_LOOKBACK_HOURS = 24

# Kerzen für den Backtest (OneHour, max. 1000 pro Abruf = ca. 6 Wochen Krypto).
CANDLE_INTERVAL = "OneHour"
CANDLE_COUNT = 1000


def leverage_for(symbol: str) -> int:
    asset_class = UNIVERSE[symbol][1]
    return LEVERAGE_OVERRIDES.get(symbol, ASSET_CLASSES[asset_class]["max_leverage"])


def cost_for(symbol: str) -> float:
    return ASSET_CLASSES[UNIVERSE[symbol][1]]["cost_pct"]


def required_move_pct(symbol: str) -> float:
    """Kursbewegung in %, die mit maximalem Hebel nötig ist, um nach Kosten
    MIN_NET_PROFIT_PCT auf den Einsatz zu erzielen.

    Netto-Rendite auf Einsatz = Hebel * (Kursbewegung - Kosten)
    => Kursbewegung = Ziel / Hebel + Kosten
    """
    return MIN_NET_PROFIT_PCT / leverage_for(symbol) + cost_for(symbol)


def stop_move_pct(symbol: str) -> float:
    """Kursbewegung gegen die Position in %, bei der der Stop greift."""
    return max(STOP_LOSS_PCT_OF_MARGIN / leverage_for(symbol) - cost_for(symbol), 0.0)
