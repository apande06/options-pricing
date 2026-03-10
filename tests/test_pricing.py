from src.black_scholes import black_scholes_call, black_scholes_put
from src.iv import implied_volatility_bisection


def test_black_scholes_call():
    price = black_scholes_call(100, 100, 1, 0.05, 0.2)
    assert abs(price - 10.4506) < 0.01


def test_black_scholes_put():
    price = black_scholes_put(100, 100, 1, 0.05, 0.2)
    assert abs(price - 5.5735) < 0.01


def test_implied_volatility_solver():
    market_price = black_scholes_call(100, 100, 1, 0.05, 0.2)
    iv = implied_volatility_bisection(market_price, 100, 100, 1, 0.05, option_type="call")
    assert iv is not None
    assert abs(iv - 0.2) < 1e-3