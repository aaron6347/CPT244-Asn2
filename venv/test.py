"""test.py
    Created by Aaron at 11-Jun-20"""
import random
ranslots = list(range(1, 300))
random.shuffle(ranslots)
print(ranslots)
x = 10
a = 0 if x == 0 else 1
print(a)

a=[(1,1),(2,0)]
print(min(a, key=lambda tup: tup[1]))

a = random.choice((0,1))
for x in range(10):
    print(random.choice((0,1)))