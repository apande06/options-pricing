# Options Pricing Dashboard

A Python project for pricing options with:

- Black-Scholes for European options
- American binomial tree pricing
- Greeks
- Implied volatility solver
- Live option-chain data using Yahoo Finance
- Streamlit dashboard for interactive analysis

## Features

- Live ticker input
- Expiration and strike selection
- Market-vs-model comparison
- Black-Scholes and American binomial pricing
- Delta, Gamma, Vega, Theta
- Implied volatility solver
- Sensitivity charts

## Project Structure

```text
2026-options-pricing-blacksholes/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── black_scholes.py
│   ├── binomial.py
│   ├── greeks.py
│   ├── iv.py
│   ├── market_data.py
│   └── main.py
└── tests/
    └── test_pricing.py