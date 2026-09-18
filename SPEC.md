# SPEC.md — Pricing rules of the oracle

Everything below was worked out by calling `quote()` with different inputs and
comparing the results. The rules are listed in the order the engine applies
them, because with this engine the order genuinely changes the answer.

All prices are rounded to 2 decimals at the very end. The engine is
deterministic, so the same inputs always give the same number back.

The full formula, in one block:

```
chargeable_weight = ceil(weight_kg / 0.5) * 0.5

price = 40.00 * chargeable_weight + 2.50 * distance_km

if category == "electronics":  price = price * 1.3
if category == "fragile":      price = price + 150.00

if price > 800.00:             price = price * 0.9

if coupon == "WELCOME10":      price = price - 100.00

return round(price, 2)
```

---

## Rule 1 — Weight is billed in half-kilo blocks, rounded up

Weight does not scale smoothly. The engine rounds the weight **up** to the next
0.5 kg and charges **40.00 per kilogram** of that rounded figure, which works
out to 20.00 per half-kilo block.

A 0.6 kg parcel and a 1.0 kg parcel therefore cost exactly the same, because
both are billed as 1.0 kg. This also means there is a minimum billable weight
of 0.5 kg, so anything from 0.1 kg to 0.5 kg is charged as 0.5 kg.

```python
quote(0.5, 100.0, "standard")   # 270.0   billed as 0.5 kg
quote(0.6, 100.0, "standard")   # 290.0   billed as 1.0 kg, one block more
quote(1.0, 100.0, "standard")   # 290.0   same as 0.6 kg
```

The 20.00 gap between the first two is one half-kilo block.

## Rule 2 — Distance is a flat 2.50 per km

Distance is not blocked or rounded. Every single kilometre costs 2.50, and the
engine responds to a 1 km change.

```python
quote(1.0, 100.0, "standard")   # 290.0
quote(1.0, 101.0, "standard")   # 292.5   exactly 2.50 more
```

## Rule 3 — There is no fixed booking fee

Weight and distance are the whole subtotal. Nothing is added on top just for
placing an order.

```python
quote(0.5, 1.0, "standard")     # 22.5
```

That is `40.00 * 0.5 + 2.50 * 1`, with nothing left over, so the base fee is 0.

So the subtotal before any adjustments is:

```
subtotal = 40.00 * chargeable_weight + 2.50 * distance_km
```

## Rule 4 — "electronics" multiplies the subtotal by 1.3

A 30 percent uplift on whatever the subtotal is. It scales with the order
rather than adding a fixed amount, which I confirmed by checking that the
**ratio** stays at 1.3 across very different price levels.

```python
quote(1.0, 10.0,  "standard")     # 65.0
quote(1.0, 10.0,  "electronics")  # 84.5    65.0 * 1.3

quote(2.0, 100.0, "standard")     # 330.0
quote(2.0, 100.0, "electronics")  # 429.0   330.0 * 1.3, same ratio
```

## Rule 5 — "fragile" adds a flat 150.00

Unlike electronics, this one does not scale. The **difference** stays at 150.00
no matter how big or small the order is.

```python
quote(1.0, 10.0,  "standard")   # 65.0
quote(1.0, 10.0,  "fragile")    # 215.0    65.0 + 150.00

quote(2.0, 100.0, "standard")   # 330.0
quote(2.0, 100.0, "fragile")    # 480.0    330.0 + 150.00, same difference
```

## Rule 6 — "books", "clothing" and "food" are priced as standard

These three are valid inputs and the engine accepts them, but they have no
price effect at all. They behave exactly like `"standard"`.

```python
quote(2.0, 100.0, "standard")   # 330.0
quote(2.0, 100.0, "books")      # 330.0
quote(2.0, 100.0, "clothing")   # 330.0
quote(2.0, 100.0, "food")       # 330.0
```

## Rule 7 — Orders above 800.00 get 10 percent off

If the running price is **strictly greater than 800.00**, the whole thing is
multiplied by 0.9.

Two details matter here:

1. The test runs on the price **after** the category adjustment, not on the raw
   weight-plus-distance subtotal. A category surcharge can push an order over
   the line on its own.
2. The comparison is strict. A price of exactly 800.00 is not discounted.

```python
quote(0.5, 312.0, "standard")   # 800.0    exactly 800.00, no discount
quote(0.5, 313.0, "standard")   # 722.25   802.50 * 0.9
```

And an example of a category triggering it, where the subtotal alone is only
700.00 and would not qualify:

```python
quote(1.0, 264.0, "standard")      # 700.0    under the line
quote(1.0, 264.0, "fragile")       # 765.0    (700 + 150) * 0.9
quote(1.0, 264.0, "electronics")   # 819.0    (700 * 1.3) * 0.9
```

Because this is a threshold rather than a smooth curve, the price can drop
when the parcel gets heavier:

```python
quote(13.5, 100.0, "standard")   # 790.0   under the line
quote(14.0, 100.0, "standard")   # 729.0   810.00 * 0.9, cheaper despite being heavier
```

## Rule 8 — "WELCOME10" takes off a flat 100.00, and it goes last

The name suggests 10 percent. It is not. It subtracts a flat **100.00**, and it
is applied after the volume discount.

```python
quote(1.0, 10.0,  "standard")                      # 65.0
quote(1.0, 10.0,  "standard", coupon="WELCOME10")  # -35.0   exactly 100.00 less

quote(2.0, 100.0, "standard")                      # 330.0
quote(2.0, 100.0, "standard", coupon="WELCOME10")  # 230.0   also exactly 100.00 less
```

The deduction is not floored at zero. A small enough order genuinely returns a
negative price, as the first example shows.

The ordering matters and is testable. Take an order whose price is 900.00
before either adjustment:

```python
quote(1.0, 344.0, "standard")                      # 810.0   900.00 * 0.9
quote(1.0, 344.0, "standard", coupon="WELCOME10")  # 710.0
```

If the coupon came first, 900.00 minus 100.00 is 800.00, which would not
qualify for the discount and would return 800.00. The engine returned 710.00,
so the discount is applied first and the coupon after it.

## Rule 9 — The coupon code is matched exactly

No trimming, no case folding, no partial matching. Anything other than the
exact string `"WELCOME10"` is ignored and priced as no coupon.

```python
quote(2.0, 100.0, "standard", coupon="WELCOME10")    # 230.0
quote(2.0, 100.0, "standard", coupon="welcome10")    # 330.0   ignored
quote(2.0, 100.0, "standard", coupon="WELCOME10 ")   # 330.0   trailing space, ignored
quote(2.0, 100.0, "standard", coupon="SAVE20")       # 330.0   unknown code, ignored
```

## Rule 10 — `express` has no effect on price

This is a real finding and not a gap in my testing. I compared express against
non-express across every combination of weight, distance, category and coupon I
could think of, and the difference was 0.00 every single time. The parameter is
accepted by the function and then ignored.

```python
quote(2.0, 100.0, "standard", express=False)   # 330.0
quote(2.0, 100.0, "standard", express=True)    # 330.0
```

---

## A full worked example

```python
quote(2.3, 400.0, "electronics", express=True, coupon="WELCOME10")
```

Step by step:

| Step              | Working                    | Running price |
| ----------------- | -------------------------- | ------------- |
| Chargeable weight | 2.3 kg rounds up to 2.5 kg |               |
| Weight charge     | 40.00 × 2.5                | 100.00        |
| Distance charge   | 2.50 × 400                 | 1100.00       |
| Category          | electronics, × 1.3         | 1430.00       |
| Express           | no effect                  | 1430.00       |
| Volume discount   | 1430.00 > 800.00, so × 0.9 | 1287.00       |
| Coupon            | WELCOME10, − 100.00        | 1187.00       |

The oracle returns **1187.0**, which matches.
