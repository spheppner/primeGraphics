def start(mode="prime",position_number=0, position2_number=0):
    import math
    z = 80 # root: math.sqrt(y)

    def isDivisible(number,divisor):
        if number % divisor == 0:
            return True
        return False

    def is_prime_number(x,pmode="prime"):
        if pmode == "prime":
            if x >= 2:
                for y in range(2,x):
                    if not ( x % y ): # x % y == 0
                        return False
            else:
                return False
            return True
        elif pmode == "position":
            for z in range(2):
                if x >= 2:
                    for y in range(2,x):
                        if not ( x % y ):
                            return False
                else:
                    return False
                if z == 0:
                    x = x//position_number
            return True
        elif pmode == "position2":
            for z in range(2):
                if x >= 2:
                    for y in range(2,x):
                        if not ( x % y ):
                            return False
                else:
                    return False
                if z == 0:
                    x = x//position_number
                    x += 10
                    x = x//position2_number
            return True
        
    primes = []
    y = 4241
    
    if mode == "prime":
        for x in range(y):
            print(x)
            if isDivisible(x, z) is True:
                primes.append("\n")
                    
            if is_prime_number(x) is True:
                primes.append("#")
            else:
                primes.append("0")
    elif mode == "position":
        for x in range(y):
            print(x)
            if isDivisible(x, z) is True:
                primes.append("\n")
                    
            if is_prime_number(x,"position") is True:
                primes.append("#")
            else:
                primes.append("0")
    elif mode == "position2":
        for x in range(y):
            print(x)
            if isDivisible(x, z) is True:
                primes.append("\n")
                    
            if is_prime_number(x,"position2") is True:
                primes.append("#")
            else:
                primes.append("0")





    with open("primes.txt", "w") as p:
        for x in primes:
            p.write(x)
        
