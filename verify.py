import random

from oracle import quote as oracle_quote, queries_used, reset_counter
from my_quote import quote as my_quote

CATEGORIES = ["standard", "electronics", "fragile", "books", "clothing", "food"]
COUPONS = ["", "WELCOME10", "welcome10", "SAVE20"]


def compare(w, d, c, e, cp, failures):
    a = oracle_quote(w, d, c, e, cp)
    b = my_quote(w, d, c, e, cp)
    if a != b:
        failures.append((w, d, c, e, cp, a, b))
    return a == b


def main():
    reset_counter()
    failures = []
    checks = 0

    random.seed(20240517)
    for _ in range(30000):
        w = round(random.uniform(0.1, 100.0), random.choice([1, 2, 3]))
        d = round(random.uniform(1.0, 5000.0), random.choice([0, 1, 2, 3]))
        compare(w, d,
                random.choice(CATEGORIES),
                random.choice([True, False]),
                random.choice(COUPONS),
                failures)
        checks += 1

    for k in range(1, 201):
        for eps in (-1e-9, -1e-6, 0.0, 1e-9, 1e-6):
            w = k * 0.5 + eps
            if not (0.1 <= w <= 100.0):
                continue
            for d in (1.0, 100.0, 312.0, 1234.567):
                for c in CATEGORIES:
                    compare(w, d, c, False, "", failures)
                    checks += 1

    d = 311.0
    while d <= 313.0:
        compare(0.5, round(d, 5), "standard", False, "", failures)
        compare(0.5, round(d, 5), "standard", False, "WELCOME10", failures)
        checks += 2
        d += 0.001

    corners = [
        (0.1, 1.0, "standard", False, ""),            # cheapest order possible
        (0.1, 1.0, "standard", False, "WELCOME10"),   # goes negative
        (100.0, 5000.0, "electronics", True, "WELCOME10"),  # most expensive
        (0.5, 312.0, "standard", False, ""),          # exactly 800.00
        (0.5, 312.004, "standard", False, ""),        # a hair over 800.00
        (13.5, 100.0, "standard", False, ""),         # just under the line
        (14.0, 100.0, "standard", False, ""),         # just over the line
        (1.0, 264.0, "electronics", False, ""),       # category pushes it over
        (1.0, 264.0, "fragile", False, ""),           # surcharge pushes it over
        (1.0, 344.0, "standard", False, "WELCOME10"), # coupon ordering case
    ]
    for t in corners:
        compare(*t, failures)
        checks += 1

    # report
    print(f"inputs compared : {checks}")
    print(f"oracle calls    : {queries_used()}")
    print(f"mismatches      : {len(failures)}")

    if failures:
        print("\nFirst few disagreements:")
        for f in failures[:20]:
            w, d, c, e, cp, a, b = f
            print(f"  w={w} d={d} {c} express={e} coupon={cp!r}"
                  f"  oracle={a}  mine={b}")
    else:
        print("\nNo disagreements. my_quote.py matches the oracle on every input tested.")


if __name__ == "__main__":
    main()