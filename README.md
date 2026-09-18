Black box reverse engineering assignment - Manav Sharma (23/EC/121)

## What's in here

oracle.py was given, everything else I wrote after probing it.

my_quote.py - my version of the pricing function, doesn't touch oracle.py at all
probes.py - the actual experiments I ran, in order, with my notes as I went
verify.py - throws a huge number of random + edge case inputs at both
functions and checks they match
SPEC.md - the rules written out properly once I'd figured them all out
NOTES.md - the 10ish bullet summary the assignment asks for

## How to run it

I'm on Python 3.15 by default and that crashed instantly when importing
oracle.py (access violation, no real error message, nothing prints). Turns out
the encoded bytecode inside oracle.py was compiled with an older Python and
doesn't load right on 3.14/3.15. Had to install 3.12 separately and run
everything with py -3.12 instead of the normal python command.

py -3.12 probes.py
py -3.12 verify.py
py -3.12 my_quote.py

verify.py takes a few seconds since it's running ~58k comparisons. output
looks like this when it's done:

inputs compared : 57964
oracle calls : 57964
mismatches : 0
No disagreements. my_quote.py matches the oracle on every input tested.

## Quick summary of what I found

weight gets rounded up to the nearest 0.5kg before it's charged, 40/kg
distance is a straight 2.5/km, nothing fancy
electronics multiplies the whole price by 1.3
fragile just adds a flat 150 on top
books/clothing/food don't do anything different from standard
if the price goes above 800 you get 10% off automatically
WELCOME10 knocks off a flat 100 (not 10%, despite the name), applied last
express does literally nothing, I checked it like 200 different ways

Full breakdown with the actual numbers is in SPEC.md, and NOTES.md has the
stuff I got wrong before I got it right (mainly: thought express did
something, thought the coupon was percentage based, thought the >800 thing
was a heavier-weight bulk rate before realizing it's price based not
weight based).
