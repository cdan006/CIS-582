import math

def num_BTC(b):
    c = b
    total = float(0)
    rate = 50
    while c>0:
        if c>210000:
            total = total + (210000*rate)
            c = c-210000
            rate = rate/2
        else:
            total = total + (c*rate)
            c = c-c
    return total

"""

def main():
    a = num_BTC(210001)
    print(a)


if __name__ == '__main__':
    main()
    
"""