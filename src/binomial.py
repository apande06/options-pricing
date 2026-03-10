import math


def american_option_binomial(S, K, T, r, sigma, N=200, option_type="call", q=0.0):
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        raise ValueError("S, K, T, and sigma must be positive.")
    if N <= 0:
        raise ValueError("N must be positive.")
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'.")

    dt = T / N
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    p = (math.exp((r - q) * dt) - d) / (u - d)
    p = max(0.0, min(1.0, p))
    discount = math.exp(-r * dt)

    stock_prices = [S * (u ** j) * (d ** (N - j)) for j in range(N + 1)]

    if option_type == "call":
        option_values = [max(price - K, 0.0) for price in stock_prices]
    else:
        option_values = [max(K - price, 0.0) for price in stock_prices]

    for i in range(N - 1, -1, -1):
        new_values = []
        for j in range(i + 1):
            stock_price = S * (u ** j) * (d ** (i - j))
            continuation = discount * (p * option_values[j + 1] + (1 - p) * option_values[j])

            if option_type == "call":
                exercise = max(stock_price - K, 0.0)
            else:
                exercise = max(K - stock_price, 0.0)

            new_values.append(max(continuation, exercise))

        option_values = new_values

    return option_values[0]