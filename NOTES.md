# Investigation summary

How I actually got to the answer, including the bits I got wrong on the way.

- **Started with one input at a time.** I fixed distance at 100 km and category
  at `"standard"`, then walked the weight up. The price moved in a clean line,
  so my first guess was a simple 40.00 per kg rate plus a fixed booking fee.

- **That guess was wrong about the weight.** The coarse sweep hid it, but 0.1 kg
  and 0.5 kg returned the same price, which a per-kg rate cannot do. Going back
  in 0.1 kg steps showed a staircase: flat, then a jump of exactly 20.00, then
  flat again, with the jumps landing on the half-kilos. Weight is rounded **up**
  to the next 0.5 kg and billed at 40.00 per kg of that figure.

- **It was also wrong about the booking fee.** I had solved for a base of 250.00
  from a single data point at 100 km. Once I ran the distance sweep I realised
  that 250.00 was just the distance charge at 100 km, and the real base fee is
  zero. A good reminder not to fit a constant from one sample.

- **Distance turned out to be the boring one.** I expected blocked pricing, so I
  checked 99, 100 and 101 km specifically, looking for a jump at the round
  number. There wasn't one. It is a flat 2.50 per km with no rounding.

- **Then the model broke at 14 kg.** The price _dropped_ from 790.00 to 729.00
  when the parcel got heavier. My first read was a cheaper bulk rate kicking in
  for heavy shipments, since the slope after that point was 36.00 per kg instead
  of 40.00.

- **The bulk-rate theory was wrong.** 36.00 is 40.00 × 0.9, which made me suspect
  a 10 percent discount rather than a new rate. If it were weight-based, a light
  parcel could never trigger it, so I tested a 0.5 kg parcel and just pushed the
  distance up instead. It got the same discount. The trigger is the **price**
  crossing 800.00, not the weight.

- **Checked whether the threshold was inclusive.** A 0.5 kg parcel at 312 km
  comes to exactly 800.00 and is _not_ discounted, while 313 km is. So the
  comparison is strictly greater than, not greater than or equal to.

- **Separated multipliers from flat fees by testing each category twice**, once
  on a cheap order and once on an expensive one. `electronics` held the same
  ratio (1.3) at both, so it is a multiplier. `fragile` held the same difference
  (150.00) at both, so it is a flat surcharge. `books`, `clothing` and `food` had
  no effect on the price at all.

- **`express` was a dead end, and that is the result.** I assumed it was a
  surcharge and went looking for it, first as a flat fee and then as a
  percentage. I ended up comparing express against non-express across 192
  combinations of weight, distance, category and coupon. The difference was 0.00
  in every single one. The flag is accepted and ignored.

- **`WELCOME10` is not 10 percent.** The name pushed me straight into assuming a
  0.9 multiplier, and the ratio on one test order looked plausible enough that I
  nearly left it there. Testing it on orders of very different sizes killed the
  idea: the ratio moved around but the difference was a constant 100.00 every
  time. It is a flat deduction, and it is not floored at zero, so a small enough
  order comes back negative.

- **Ordering was the last thing to pin down.** Three rules can move the price, so
  I built cases where the sequence changes the answer. An order with a 700.00
  subtotal gets discounted once a category surcharge pushes it past 800.00, so
  category runs before the discount test. An order at 900.00 returns 710.00 with
  the coupon rather than 800.00, so the coupon runs after the discount. Final
  order is weight and distance, then category, then volume discount, then coupon.

- **Verified rather than assumed.** `verify.py` compares `my_quote.py` against
  the oracle on roughly 58,000 inputs, including random draws across the full
  documented ranges, every half-kilo boundary nudged either side, and a fine walk
  across the 800.00 discount line. Zero disagreements.
