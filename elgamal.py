import random

from params import p
from params import g

q = (p - 1) / 2
#m = random.randint(1, p)

def keygen():
    if q == None:
        a = random.randint(1, p)
    else:
        a = random.randint(1, q)
    sk = a
    h = pow(g, a, p)
    pk = h
    return pk, sk


def encrypt(pk, m):
    c1 = 0
    c2 = 0
    r = random.randint(1,q)
    c1 = pow(g,r,p)
    step = pow(pk,r,p)
    c2 = (step*m)%p

    return [c1, c2]

def decrypt(sk, c):
    return sk

"""
def decrypt(sk, c):
    c1, c2 = c
    a = pow(c1, sk,p)
    x = modinv(a,p)
    m = (c2 * x)%p
    return m


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1 and g != -1:
        raise Exception('No inverse')
    else:
        return x % m

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
"""
