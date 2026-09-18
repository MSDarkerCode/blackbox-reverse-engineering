"""
my_quote.py

My reconstruction of the pricing engine hidden inside oracle.py.

Everything here was worked out by calling oracle.quote() with different
inputs and watching how the number moved. This file does not import
oracle and does not depend on it in any way.

Recovered formula:

    chargeable_weight = weight rounded UP to the next 0.5 kg
    price = 40.00 * chargeable_weight + 2.50 * distance_km

    electronics -> price * 1.3
    fragile     -> price + 150.00

    if price > 800.00 -> price * 0.9

    coupon "WELCOME10" -> price - 100.00

    return price rounded to 2 decimals
"""
import math

WEIGHT_STEP_KG = 0.5           # weight is billed in whole half-kilos
RATE_PER_KG = 40.0
RATE_PER_KM = 2.5

ELECTRONICS_MULTIPLIER = 1.3
FRAGILE_SURCHARGE = 150.0

VOLUME_DISCOUNT_THRESHOLD = 800.0   # strictly greater than, not >=
VOLUME_DISCOUNT_MULTIPLIER = 0.9

COUPON_CODE = "WELCOME10"
COUPON_AMOUNT = 100.0


def chargeable_weight(weight_kg):
    """Weight is not billed continuously. It is rounded up to the next 0.5 kg."""
    return math.ceil(weight_kg / WEIGHT_STEP_KG) * WEIGHT_STEP_KG


def quote(weight_kg, distance_km, category, express=False, coupon=""):
    """
    Same signature and same return value as oracle.quote().

    Note on `express`: the parameter is accepted but has no effect on the
    price. That is not an oversight on my part, it is what the oracle does.
    See NOTES.md.
    """
    price = chargeable_weight(weight_kg) * RATE_PER_KG
    price += distance_km * RATE_PER_KM

    if category == "electronics":
        price *= ELECTRONICS_MULTIPLIER
    elif category == "fragile":
        price += FRAGILE_SURCHARGE

    # Applied after the category adjustment, and it is a strict comparison:
    # a price of exactly 800.00 does NOT get the discount.
    if price > VOLUME_DISCOUNT_THRESHOLD:
        price *= VOLUME_DISCOUNT_MULTIPLIER

    # Coupon is last, and it is a flat deduction, not a percentage.
    if coupon == COUPON_CODE:
        price -= COUPON_AMOUNT

    return round(price, 2)


if __name__ == "__main__":
    print(quote(2.0, 100.0, "standard"))                                  # 330.0
    print(quote(2.0, 100.0, "electronics"))                               # 429.0
    print(quote(1.0, 500.0, "fragile", express=True, coupon="WELCOME10")) # 1196.0