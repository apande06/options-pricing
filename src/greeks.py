import math
from scipy.stats import norm
from src.black_scholes import d1, d2


def delta_call(S, K, T, r, sigma, q=0.0):
    return math.exp(-q * T) * norm.cdf(d1(S, K, T, r, sigma, q))


def delta_put(S, K, T, r, sigma, q=0.0):
    return math.exp(-q * T) * (norm.cdf(d1(S, K, T, r, sigma, q)) - 1)


def gamma(S, K, T, r, sigma, q=0.0):
    D1 = d1(S, K, T, r, sigma, q)
    return math.exp(-q * T) * norm.pdf(D1) / (S * sigma * math.sqrt(T))


def vega(S, K, T, r, sigma, q=0.0):
    D1 = d1(S, K, T, r, sigma, q)
    return S * math.exp(-q * T) * norm.pdf(D1) * math.sqrt(T)


def theta_call(S, K, T, r, sigma, q=0.0):
    D1 = d1(S, K, T, r, sigma, q)
    D2 = d2(S, K, T, r, sigma, q)
    term1 = -(S * norm.pdf(D1) * sigma * math.exp(-q * T)) / (2 * math.sqrt(T))
    term2 = -r * K * math.exp(-r * T) * norm.cdf(D2)
    term3 = q * S * math.exp(-q * T) * norm.cdf(D1)
    return term1 + term2 + term3


def theta_put(S, K, T, r, sigma, q=0.0):
    D1 = d1(S, K, T, r, sigma, q)
    D2 = d2(S, K, T, r, sigma, q)
    term1 = -(S * norm.pdf(D1) * sigma * math.exp(-q * T)) / (2 * math.sqrt(T))
    term2 = r * K * math.exp(-r * T) * norm.cdf(-D2)
    term3 = -q * S * math.exp(-q * T) * norm.cdf(-D1)
    return term1 + term2 + term3