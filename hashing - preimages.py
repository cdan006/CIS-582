import hashlib
import random
import string

def hash_preimage(target_string):
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return
    #nonce = b'\x00'
    target_string_len = len(target_string)
    letters = string.ascii_lowercase
    nonce_match = None
    while nonce_match!=target_string:
        x_string = ''.join(random.choice(letters) for i in range(random.randint(1, 20)))
        x_sha = hashlib.sha256(x_string.encode('utf-8')).hexdigest()
        n = int(x_sha, 16)
        bStr = ''
        while n > 0:
            bStr = str(n % 2) + bStr
            n = n >> 1
        nonce = str(bStr)
        nonce_match = nonce[-target_string_len:]
        if nonce_match == target_string:
            return (x_string)


def main():

    print(hash_preimage('01'))

if __name__ == '__main__':
    main()