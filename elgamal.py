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
    c2 = (pow(pk,r)*m)%p

    return [c1, c2]


def decrypt(sk, c):
    c1, c2 = c
    a = pow(c1, sk)
    #a = pow(c1,sk,p)
    x = pow(a,-1,p)
    m = (c2 * x)%p


    #power = p - 1 - sk
    #d = pow(c1,power,p)
    #m = (c2 * pow(d,-1, p)) % p

    #m = (c1/pow(c2,sk))%p

    return m
