from datetime import datetime
import pandas as pd
import yfinance as yf


def get_ticker_object(ticker: str):
    if not ticker or not ticker.strip():
        raise ValueError("Ticker cannot be empty.")
    return yf.Ticker(ticker.strip().upper())


def get_spot_price(ticker: str) -> float:
    tk = get_ticker_object(ticker)

    try:
        info = tk.fast_info
        for key in ["lastPrice", "last_price", "regularMarketPrice"]:
            value = info.get(key)
            if value is not None:
                return float(value)
    except Exception:
        pass

    hist = tk.history(period="5d")
    if hist.empty:
        raise ValueError("Could not retrieve recent price history.")
    return float(hist["Close"].dropna().iloc[-1])


def get_expirations(ticker: str):
    tk = get_ticker_object(ticker)
    expirations = list(tk.options)
    if not expirations:
        raise ValueError("No option expirations found for this ticker.")
    return expirations


def get_option_chain(ticker: str, expiration: str, option_type: str = "call") -> pd.DataFrame:
    tk = get_ticker_object(ticker)
    chain = tk.option_chain(expiration)

    if option_type == "call":
        df = chain.calls.copy()
    else:
        df = chain.puts.copy()

    if df.empty:
        raise ValueError("No option data found.")

    numeric_cols = [
        "strike",
        "lastPrice",
        "bid",
        "ask",
        "volume",
        "openInterest",
        "impliedVolatility",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "lastTradeDate" in df.columns:
        df["lastTradeDate"] = pd.to_datetime(df["lastTradeDate"], errors="coerce")

    return df.sort_values("strike").reset_index(drop=True)


def days_to_expiration(expiration: str) -> int:
    exp = datetime.strptime(expiration, "%Y-%m-%d").date()
    today = datetime.today().date()
    return max((exp - today).days, 0)


def year_fraction_from_expiration(expiration: str) -> float:
    return days_to_expiration(expiration) / 365.0