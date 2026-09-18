import math

WEIGHT_STEP_KG = 0.5          
RATE_PER_KG = 40.0
RATE_PER_KM = 2.5

ELECTRONICS_MULTIPLIER = 1.3
FRAGILE_SURCHARGE = 150.0

VOLUME_DISCOUNT_THRESHOLD = 800.0
VOLUME_DISCOUNT_MULTIPLIER = 0.9

COUPON_CODE = "WELCOME10"
COUPON_AMOUNT = 100.0


def chargeable_weight(weight_kg):
    return math.ceil(weight_kg / WEIGHT_STEP_KG) * WEIGHT_STEP_KG


def quote(weight_kg, distance_km, category, express=False, coupon=""):
    
    price = chargeable_weight(weight_kg) * RATE_PER_KG
    price += distance_km * RATE_PER_KM

    if category == "electronics":
        price *= ELECTRONICS_MULTIPLIER
    elif category == "fragile":
        price += FRAGILE_SURCHARGE
    
    if price > VOLUME_DISCOUNT_THRESHOLD:
        price *= VOLUME_DISCOUNT_MULTIPLIER

    if coupon == COUPON_CODE:
        price -= COUPON_AMOUNT

    return round(price, 2)


if __name__ == "__main__":
    print(quote(2.0, 100.0, "standard"))                                  
    print(quote(2.0, 100.0, "electronics"))                               
    print(quote(1.0, 500.0, "fragile", express=True, coupon="WELCOME10"))