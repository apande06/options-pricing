import math
from scipy.stats import norm


def _validate_inputs(S, K, T, sigma):
    if S <= 0:
        raise ValueError("Stock price S must be positive.")
    if K <= 0:
        raise ValueError("Strike price K must be positive.")
    if T <= 0:
        raise ValueError("Time to expiration T must be positive.")
    if sigma <= 0:
        raise ValueError("Volatility sigma must be positive.")


def d1(S, K, T, r, sigma, q=0.0):
    _validate_inputs(S, K, T, sigma)
    return (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))


def d2(S, K, T, r, sigma, q=0.0):
    return d1(S, K, T, r, sigma, q) - sigma * math.sqrt(T)


def black_scholes_call(S, K, T, r, sigma, q=0.0):
    D1 = d1(S, K, T, r, sigma, q)
    D2 = d2(S, K, T, r, sigma, q)
    return S * math.exp(-q * T) * norm.cdf(D1) - K * math.exp(-r * T) * norm.cdf(D2)


def black_scholes_put(S, K, T, r, sigma, q=0.0):
    D1 = d1(S, K, T, r, sigma, q)
    D2 = d2(S, K, T, r, sigma, q)
    return K * math.exp(-r * T) * norm.cdf(-D2) - S * math.exp(-q * T) * norm.cdf(-D1)