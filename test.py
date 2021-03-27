import numpy as np
cases = int(input())

def rec_cost(arr, target):
    if len(arr) == 0:
        return None
    if target == 0:
        return arr
    left = len(arr) - 1
    if left >= target:
        return np.append(
            np.flip(arr[0:target + 1]),
            arr[target + 1:])
    else:
        el = arr[0]
        new_arr = rec_cost(arr[1:len(arr)], target - left)
        if new_arr is None:
            return None
        return np.append(
            np.flip(new_arr), el
        )

def rev(arr, target):
    cost = len(arr) - 1
    if cost > target:
        return None
    return rec_cost(arr, target - cost)

case = 0
for _ in range(cases):
    case += 1
    t, c = map(int, input().split(' '))
    arr = np.arange(1, t + 1)
    arr = rev(arr, c)
    if arr is None:
        print(f"Case #{case}: IMPOSSIBLE")
    else:
        arr = ' '.join(str(x) for x in arr)
        print(f"Case #{case}: {arr}")