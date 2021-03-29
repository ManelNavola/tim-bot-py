import random

tiers = {
    'common': 100,
    'uncommon': 60,
    'rare': 25,
    'epic': 5,
    'legendary': 1
}

number = 5

def run():
    for _ in range(number):
        print(random.choices(population=list(tiers.keys()), weights=list(tiers.values()))[0])

keys = list(tiers.keys())
values = list(tiers.values())
values_sum = sum(values)
values = [x / values_sum for x in values]

tiers = {keys[i]: values[i] for i in range(len(keys))}
for k, v in tiers.items():
    print(f"{k}: {v:.2%}")

while True:
    n = input("Insert number or press enter: ")
    if n:
        number = int(n)
    run()
    