import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.black_scholes import black_scholes_call, black_scholes_put
from src.binomial import american_option_binomial
from src.greeks import delta_call, delta_put, gamma, vega, theta_call, theta_put
from src.iv import implied_volatility_bisection
from src.market_data import (
    get_spot_price,
    get_expirations,
    get_option_chain,
    year_fraction_from_expiration,
    days_to_expiration,
)

st.set_page_config(page_title="Options Pricing Dashboard", layout="wide")

st.title("Options Pricing Dashboard")
st.caption("Black-Scholes, American Binomial, Live Option Chain, and Implied Volatility")

with st.sidebar:
    st.header("Inputs")
    ticker = st.text_input("Ticker", value="SPY").upper().strip()
    option_type = st.selectbox("Option Type", ["call", "put"])
    r = st.number_input("Risk-free Rate (decimal)", min_value=0.0, max_value=1.0, value=0.045, step=0.001)
    q = st.number_input("Dividend Yield (decimal)", min_value=0.0, max_value=1.0, value=0.0, step=0.001)
    steps = st.slider("Binomial Steps", min_value=50, max_value=1000, value=200, step=50)

spot = None
expirations = []
chain = pd.DataFrame()

try:
    spot = get_spot_price(ticker)
    expirations = get_expirations(ticker)
except Exception as e:
    st.error(f"Market data error: {e}")

if spot is not None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Spot Price", f"{spot:.2f}")
    c2.metric("Ticker", ticker)
    c3.metric("Expirations Found", len(expirations))

if expirations:
    selected_exp = st.selectbox("Expiration", expirations)
    T = year_fraction_from_expiration(selected_exp)
    dte = days_to_expiration(selected_exp)

    try:
        chain = get_option_chain(ticker, selected_exp, option_type)
    except Exception as e:
        st.error(f"Option chain error: {e}")

    if not chain.empty:
        strikes = chain["strike"].dropna().tolist()
        selected_strike = st.selectbox("Strike", strikes, index=min(len(strikes) // 2, len(strikes) - 1))

        selected_row = chain.loc[chain["strike"] == selected_strike].head(1)
        if selected_row.empty:
            st.stop()

        row = selected_row.iloc[0]

        market_last = float(row["lastPrice"]) if pd.notna(row.get("lastPrice")) else None
        bid = float(row["bid"]) if pd.notna(row.get("bid")) else None
        ask = float(row["ask"]) if pd.notna(row.get("ask")) else None
        yahoo_iv = float(row["impliedVolatility"]) if pd.notna(row.get("impliedVolatility")) else None

        safe_chain_iv = None
        if yahoo_iv is not None and 0.05 <= float(yahoo_iv) <= 3.0:
            safe_chain_iv = float(yahoo_iv)

        default_sigma = safe_chain_iv if safe_chain_iv is not None else 0.25
        default_sigma = min(5.0, max(0.0001, default_sigma))

        manual_sigma = st.number_input(
            "Manual Volatility Override (decimal)",
            min_value=0.0001,
            max_value=5.0,
            value=default_sigma,
            step=0.01,
        )

        if yahoo_iv is not None and 0.05 <= float(yahoo_iv) <= 3.0:
            safe_chain_iv = float(yahoo_iv)
        else:
            safe_chain_iv = None

        default_sigma = 0.25
        manual_sigma = st.number_input(
            "Volatility Used for Pricing (decimal)",
            min_value=0.0001,
            max_value=5.0,
            value=default_sigma,
            step=0.01,
        )

        sigma = manual_sigma

        implied_vol = None
        if market_last is not None and market_last > 0:
            implied_vol = implied_volatility_bisection(
                market_last,
                spot,
                selected_strike,
                T,
                r,
                option_type=option_type,
                q=q,
            )

        if T <= 0:
            st.warning("This option expires today or has no remaining time.")
            st.stop()

        if option_type == "call":
            bs_price = black_scholes_call(spot, selected_strike, T, r, sigma, q)
            bs_delta = delta_call(spot, selected_strike, T, r, sigma, q)
            bs_theta = theta_call(spot, selected_strike, T, r, sigma, q)
        else:
            bs_price = black_scholes_put(spot, selected_strike, T, r, sigma, q)
            bs_delta = delta_put(spot, selected_strike, T, r, sigma, q)
            bs_theta = theta_put(spot, selected_strike, T, r, sigma, q)

        am_price = american_option_binomial(
            spot,
            selected_strike,
            T,
            r,
            sigma,
            N=steps,
            option_type=option_type,
            q=q,
        )

        implied_vol = None
        if market_last is not None and market_last > 0:
            implied_vol = implied_volatility_bisection(
                market_last,
                spot,
                selected_strike,
                T,
                r,
                option_type=option_type,
                q=q,
            )

        intrinsic = max(spot - selected_strike, 0.0) if option_type == "call" else max(selected_strike - spot, 0.0)
        reference_price = market_last if market_last is not None else bs_price
        time_value = max(reference_price - intrinsic, 0.0)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Black-Scholes", f"{bs_price:.4f}")
        m2.metric("American Binomial", f"{am_price:.4f}")
        m3.metric("Market Last", "N/A" if market_last is None else f"{market_last:.4f}")
        m4.metric("Days to Expiration", str(dte))

        m5, m6, m7, m8 = st.columns(4)
        m5.metric("Delta", f"{bs_delta:.4f}")
        m6.metric("Gamma", f"{gamma(spot, selected_strike, T, r, sigma, q):.4f}")
        m7.metric("Vega", f"{vega(spot, selected_strike, T, r, sigma, q):.4f}")
        m8.metric("Theta", f"{bs_theta:.4f}")

        m9, m10, m11, m12 = st.columns(4)
        m9.metric("Intrinsic Value", f"{intrinsic:.4f}")
        m10.metric("Time Value", f"{time_value:.4f}")
        m11.metric("Chain IV", "N/A" if yahoo_iv is None else f"{yahoo_iv:.4f}")
        m12.metric("Solved IV", "N/A" if implied_vol is None else f"{implied_vol:.4f}")

        st.subheader("Market vs Model Comparison")
        compare_rows = []

        if market_last is not None:
            compare_rows.append({
                "Model": "Black-Scholes",
                "Model Price": bs_price,
                "Market Price": market_last,
                "Dollar Difference": bs_price - market_last,
                "Percent Difference": ((bs_price - market_last) / market_last) * 100 if market_last != 0 else None,
            })
            compare_rows.append({
                "Model": "American Binomial",
                "Model Price": am_price,
                "Market Price": market_last,
                "Dollar Difference": am_price - market_last,
                "Percent Difference": ((am_price - market_last) / market_last) * 100 if market_last != 0 else None,
            })

        if compare_rows:
            st.dataframe(pd.DataFrame(compare_rows), use_container_width=True)

        st.subheader("Selected Option Snapshot")
        snapshot = pd.DataFrame([{
            "Ticker": ticker,
            "Option Type": option_type,
            "Expiration": selected_exp,
            "Strike": selected_strike,
            "Spot": spot,
            "Bid": bid,
            "Ask": ask,
            "Last": market_last,
            "Sigma Used": sigma,
            "Risk-Free Rate": r,
            "Dividend Yield": q,
        }])
        st.dataframe(snapshot, use_container_width=True)

        st.subheader("Live Chain Preview")
        preview_cols = [col for col in ["contractSymbol", "strike", "bid", "ask", "lastPrice", "volume", "openInterest", "impliedVolatility"] if col in chain.columns]
        st.dataframe(chain[preview_cols].head(20), use_container_width=True)

        st.subheader("Sensitivity Charts")

        stock_range = [spot * (0.7 + i * 0.03) for i in range(21)]
        prices_vs_stock = []
        for stock_val in stock_range:
            if option_type == "call":
                price = black_scholes_call(stock_val, selected_strike, T, r, sigma, q)
            else:
                price = black_scholes_put(stock_val, selected_strike, T, r, sigma, q)
            prices_vs_stock.append(price)

        fig1, ax1 = plt.subplots()
        ax1.plot(stock_range, prices_vs_stock)
        ax1.set_xlabel("Underlying Price")
        ax1.set_ylabel("Option Price")
        ax1.set_title("Option Price vs Underlying Price")
        st.pyplot(fig1)

        vol_range = [0.05 + i * 0.025 for i in range(20)]
        prices_vs_vol = []
        for vol in vol_range:
            if option_type == "call":
                price = black_scholes_call(spot, selected_strike, T, r, vol, q)
            else:
                price = black_scholes_put(spot, selected_strike, T, r, vol, q)
            prices_vs_vol.append(price)

        fig2, ax2 = plt.subplots()
        ax2.plot(vol_range, prices_vs_vol)
        ax2.set_xlabel("Volatility")
        ax2.set_ylabel("Option Price")
        ax2.set_title("Option Price vs Volatility")
        st.pyplot(fig2)

        time_range = [max(1 / 365, T * x / 20) for x in range(1, 21)]
        prices_vs_time = []
        for t in time_range:
            if option_type == "call":
                price = black_scholes_call(spot, selected_strike, t, r, sigma, q)
            else:
                price = black_scholes_put(spot, selected_strike, t, r, sigma, q)
            prices_vs_time.append(price)

        fig3, ax3 = plt.subplots()
        ax3.plot(time_range, prices_vs_time)
        ax3.set_xlabel("Time to Expiration (Years)")
        ax3.set_ylabel("Option Price")
        ax3.set_title("Option Price vs Time to Expiration")
        st.pyplot(fig3)
else:
    st.info("Enter a valid ticker to load option data.")