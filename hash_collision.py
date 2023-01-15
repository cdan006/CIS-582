import hashlib
import os
import random
import string

def hash_collision(k):
    if not isinstance(k, int):
        print("hash_collision expects an integer")
        return (b'\x00', b'\x00')
    if k < 0:
        print("Specify a positive number of bits")
        return (b'\x00', b'\x00')

    # Collision finding code goes here
    letters = string.ascii_lowercase
    x_string = ''.join(random.choice(letters) for i in range(random.randint(1,20)))
    x_sha = hashlib.sha256(x_string.encode('utf-8')).hexdigest()
    n = int(x_sha, 16)
    bStr = ''
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    res = str(bStr)
    x_match_bytes = res[:-k]
    y_match_bytes = None
    while x_match_bytes!=y_match_bytes:
        y_string = ''.join(random.choice(letters) for i in range(random.randint(1, 20)))
        y_sha = hashlib.sha256(y_string.encode('utf-8')).hexdigest()
        n = int(x_sha, 16)
        bStr = ''
        while n > 0:
            bStr = str(n % 2) + bStr
            n = n >> 1
        res = str(bStr)
        y_match_bytes = res[:-k]
    x = x_string.encode('utf-8')
    y = y_string.encode('utf-8')
    return (x, y)


def main():
    """
    word = "Bitcoin"
    print(hashlib.sha256(word.encode('utf-8')).hexdigest())
    l = random.randint(1,20)
    letters = string.ascii_lowercase
    print(''.join(random.choice(letters) for i in range(l)))
    import hashlib
    str = "Bitcoin"
    m = hashlib.sha256()
    for c in str:
        m.update(c.encode('utf-8'))
    print(m.hexdigest())
    """
    print(hash_collision(2))



if __name__ == '__main__':
    main()
