from src.black_scholes import black_scholes_call, black_scholes_put
from src.binomial import american_option_binomial
from src.greeks import delta_call, delta_put, gamma, vega


def main():
    print("Options Pricing Engine")
    print("----------------------")

    S = float(input("Enter stock price (S): "))
    K = float(input("Enter strike price (K): "))
    T = float(input("Enter time to expiration in years (T): "))
    r = float(input("Enter risk-free rate (r, decimal): "))
    sigma = float(input("Enter volatility (sigma, decimal): "))
    q = float(input("Enter dividend yield (q, decimal, use 0 if none): "))

    print("\nChoose model:")
    print("1. Black-Scholes European Call")
    print("2. Black-Scholes European Put")
    print("3. American Binomial Call")
    print("4. American Binomial Put")

    choice = input("Enter choice (1/2/3/4): ")

    if choice == "1":
        price = black_scholes_call(S, K, T, r, sigma, q)
        print(f"\nEuropean Call Price: {price:.4f}")
        print(f"Delta: {delta_call(S, K, T, r, sigma, q):.4f}")
        print(f"Gamma: {gamma(S, K, T, r, sigma, q):.4f}")
        print(f"Vega: {vega(S, K, T, r, sigma, q):.4f}")

    elif choice == "2":
        price = black_scholes_put(S, K, T, r, sigma, q)
        print(f"\nEuropean Put Price: {price:.4f}")
        print(f"Delta: {delta_put(S, K, T, r, sigma, q):.4f}")
        print(f"Gamma: {gamma(S, K, T, r, sigma, q):.4f}")
        print(f"Vega: {vega(S, K, T, r, sigma, q):.4f}")

    elif choice == "3":
        price = american_option_binomial(S, K, T, r, sigma, N=200, option_type="call", q=q)
        print(f"\nAmerican Call Price: {price:.4f}")

    elif choice == "4":
        price = american_option_binomial(S, K, T, r, sigma, N=200, option_type="put", q=q)
        print(f"\nAmerican Put Price: {price:.4f}")

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()