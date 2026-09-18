import math

from oracle import quote, queries_used, reset_counter


def rule(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


rule("1. Baseline")

print("quote(2.0, 100.0, 'standard') =", quote(2.0, 100.0, "standard"))
print("Starting point. Now I change one input at a time and watch the delta.")


rule("2. Weight, coarse sweep (distance fixed at 100 km, standard)")

prev = None
for w in [0.1, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]:
    p = quote(w, 100.0, "standard")
    delta = "-" if prev is None else round(p - prev, 2)
    print(f"  weight {w:>5} kg  ->  {p:>8}   (delta {delta})")
    prev = p

print("\n  Looks linear at 40.00 per kg. But 0.1 kg and 0.5 kg cost the same,")
print("  which a straight per-kg rate would not do. Worth a closer look.")


rule("3. Weight, fine sweep in 0.1 kg steps")

prev = None
for i in range(1, 22):
    w = round(i * 0.1, 2)
    p = quote(w, 100.0, "standard")
    jump = "" if prev is None or p == prev else "   <-- step up"
    print(f"  weight {w:>4} kg  ->  {p:>8}{jump}")
    prev = p

print("\n  The price is flat, then jumps by 20.00, then flat again.")
print("  Steps land at 0.5 / 1.0 / 1.5 / 2.0 kg, and 20.00 is half of 40.00.")
print("  So weight is billed in whole 0.5 kg blocks, rounded UP:")
print("      chargeable_weight = ceil(weight / 0.5) * 0.5")


rule("4. Distance (weight fixed at 1.0 kg, standard)")

prev = None
for d in [1.0, 2.0, 10.0, 50.0, 99.0, 100.0, 101.0, 200.0, 300.0]:
    p = quote(1.0, d, "standard")
    delta = "-" if prev is None else round(p - prev, 2)
    print(f"  distance {d:>7} km  ->  {p:>9}   (delta {delta})")
    prev = p

print("\n  Straight line, 2.50 per km, and it reacts to a single extra km.")
print("  No block rounding on distance, unlike weight.")


rule("5. Solving for a base fee")

p = quote(0.5, 1.0, "standard")
predicted = 0.5 * 40.0 + 1.0 * 2.5
print(f"  cheapest possible order, quote(0.5, 1.0, 'standard') = {p}")
print(f"  40.00 * 0.5 kg + 2.50 * 1 km                        = {predicted}")
print("\n  They match, so there is no flat booking fee. Base is zero.")
print("      subtotal = 40.00 * chargeable_weight + 2.50 * distance_km")


rule("6. Something breaks the linear model around 14 kg")

prev = None
for i in range(26, 30):
    w = i * 0.5
    p = quote(w, 100.0, "standard")
    delta = "-" if prev is None else round(p - prev, 2)
    print(f"  weight {w:>5} kg  ->  {p:>8}   (delta {delta})")
    prev = p

print("\n  The price goes DOWN when the parcel gets heavier. That is a discount")
print("  switching on, not a new weight rate.")
print("  13.5 kg subtotal = 790.00 (no discount), 14.0 kg subtotal = 810.00")
print("  810.00 * 0.9 = 729.00, which is exactly what came back.")
print("  Hypothesis: the discount triggers on the PRICE, not on the weight.")


rule("7. Same discount reached through distance (weight fixed at 0.5 kg)")


def subtotal(w, d):
    return 40.0 * (math.ceil(w / 0.5) * 0.5) + 2.5 * d


for d in [300.0, 311.0, 312.0, 313.0, 320.0]:
    p = quote(0.5, d, "standard")
    s = subtotal(0.5, d)
    print(f"  distance {d:>6} km  subtotal {s:>8.2f}  ->  oracle {p:>8}"
          f"   (0.9x would be {round(s * 0.9, 2)})")

print("\n  Confirmed. A light 0.5 kg parcel gets the same discount once its")
print("  subtotal crosses the line, so it is price-driven, not weight-driven.")
print("  Note 312 km gives a subtotal of exactly 800.00 and is NOT discounted,")
print("  so the test is strictly greater than 800, not >=.")


rule("8. Categories, tested at two very different price levels")

cats = ["standard", "electronics", "fragile", "books", "clothing", "food"]

for (w, d) in [(1.0, 10.0), (2.0, 100.0)]:
    base = quote(w, d, "standard")
    print(f"\n  weight {w} kg, distance {d} km, standard = {base}")
    for c in cats:
        p = quote(w, d, c)
        print(f"    {c:>12}  {p:>9}   difference {round(p - base, 2):>8}"
              f"   ratio {round(p / base, 4)}")

print("\n  books, clothing and food are priced exactly like standard.")
print("  electronics keeps the same RATIO (1.3) at both price levels -> multiplier.")
print("  fragile keeps the same DIFFERENCE (150.00) at both levels -> flat surcharge.")


rule("9. Express flag")

deltas = set()
checked = 0
for w in [0.5, 2.0, 14.0, 60.0]:
    for d in [1.0, 100.0, 312.0, 2000.0]:
        for c in cats:
            for cp in ["", "WELCOME10"]:
                a = quote(w, d, c, False, cp)
                b = quote(w, d, c, True, cp)
                deltas.add(round(b - a, 2))
                checked += 1

print(f"  compared express vs non-express across {checked} input combinations")
print(f"  set of every price difference observed: {deltas}")
print("\n  Express never changes the price. The parameter is accepted and ignored.")


rule("10. Coupon WELCOME10")

for (w, d) in [(1.0, 10.0), (2.0, 100.0), (1.0, 264.0)]:
    a = quote(w, d, "standard")
    b = quote(w, d, "standard", coupon="WELCOME10")
    print(f"  {a:>8} -> {b:>8}   difference {round(b - a, 2):>8}"
          f"   ratio {round(b / a, 4)}")

print("\n  The DIFFERENCE is a constant -100.00 while the ratio moves all over")
print("  the place. So the coupon is a flat deduction, not a 10 percent cut,")
print("  despite the name.")

print("\n  Other codes:")
for cp in ["", "WELCOME10", "welcome10", "WELCOME", "SAVE20", "WELCOME10 "]:
    print(f"    coupon={cp!r:<14} -> {quote(2.0, 100.0, 'standard', coupon=cp)}")
print("  Only the exact uppercase string works. No partial or fuzzy matching.")

print("\n  And it is not clamped at zero:")
print("    quote(0.1, 1.0, 'standard', coupon='WELCOME10') =",
      quote(0.1, 1.0, "standard", coupon="WELCOME10"))


rule("11. Order of operations")

print("  (a) Does the discount see the category adjustment?")
print("      Pick a subtotal of 700.00, which is under the 800.00 line.")
print("        standard    (1.0 kg, 264 km) =", quote(1.0, 264.0, "standard"))
print("        electronics                  =", quote(1.0, 264.0, "electronics"))
print("          700 * 1.3 = 910.00 with no discount, or 819.00 with it")
print("        fragile                      =", quote(1.0, 264.0, "fragile"))
print("          700 + 150 = 850.00 with no discount, or 765.00 with it")
print("      Both came back discounted, so category is applied FIRST and the")
print("      800.00 test runs on the adjusted price.")

print("\n  (b) Does the coupon come before or after the discount?")
print("      Pick a subtotal of 900.00.")
print("        standard   (1.0 kg, 344 km)            =", quote(1.0, 344.0, "standard"))
print("        same with WELCOME10                    =",
      quote(1.0, 344.0, "standard", coupon="WELCOME10"))
print("          coupon first : (900 - 100) = 800.00, no discount -> 800.00")
print("          discount first: 900 * 0.9 = 810.00, then -100 -> 710.00")
print("      The answer was 710.00, so the coupon is applied LAST.")

print("\n  Final order:  weight + distance  ->  category  ->  volume discount  ->  coupon")


rule("12. Spot check against my_quote.py")

try:
    from my_quote import quote as mine
except ImportError:
    print("  my_quote.py not found, skipping.")
else:
    samples = [
        (2.0, 100.0, "standard", False, ""),
        (0.1, 1.0, "standard", False, ""),
        (2.3, 100.0, "electronics", False, ""),
        (1.0, 10.0, "fragile", True, ""),
        (14.0, 100.0, "books", False, ""),
        (1.0, 344.0, "standard", False, "WELCOME10"),
        (100.0, 5000.0, "electronics", True, "WELCOME10"),
    ]
    print(f"  {'inputs':<52}{'oracle':>10}{'mine':>10}   ok")
    for s in samples:
        a = quote(*s)
        b = mine(*s)
        label = f"w={s[0]}, d={s[1]}, {s[2]}, express={s[3]}, coupon={s[4]!r}"
        print(f"  {label:<52}{a:>10}{b:>10}   {'yes' if a == b else 'NO'}")

print()
print("=" * 72)
print(f"Total oracle queries used in this run: {queries_used()}")
print("=" * 72)