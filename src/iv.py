from src.black_scholes import black_scholes_call, black_scholes_put


def implied_volatility_bisection(
    market_price,
    S,
    K,
    T,
    r,
    option_type="call",
    q=0.0,
    low=1e-4,
    high=5.0,
    tol=1e-6,
    max_iter=200,
):
    if market_price <= 0:
        return None

    def model_price(vol):
        if option_type == "call":
            return black_scholes_call(S, K, T, r, vol, q)
        return black_scholes_put(S, K, T, r, vol, q)

    try:
        low_price = model_price(low)
        high_price = model_price(high)
    except Exception:
        return None

    if market_price < low_price or market_price > high_price:
        return None

    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        price = model_price(mid)

        if abs(price - market_price) < tol:
            return mid

        if price < market_price:
            low = mid
        else:
            high = mid

    return 0.5 * (low + high)