primes = [2]
curr = 2

#max = input("Maximum? ", int)
max = 250

while curr < max:
    curr += 1
    
    flag = False
    for p in primes:
        if curr % p == 0:
            flag = True
            break
    if flag:
        continue

    primes.append(curr)

print ", ".join(map(str, primes))
