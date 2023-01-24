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
    c1, c2 = c
    a = pow(c1, sk)
    #a = pow(c1,sk,p)
    x = pow(a,-1,p)
    m = (c2 * x)%p

    return m
