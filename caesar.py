def encrypt(key, plaintext):
    ciphertext = ""
    z_ascii = ord("Z")
    a_ascii = ord("A")
    for x in plaintext:
        new_letter = ord(x) + key
        if new_letter > z_ascii:
            new_letter = new_letter - 26
        if new_letter < a_ascii:
            new_letter = new_letter + 26
        ciphertext = ciphertext + chr(new_letter)
    return ciphertext


def decrypt(key, ciphertext):
    plaintext = ""
    z_ascii = ord("Z")
    a_ascii = ord("A")
    for x in ciphertext:
        new_letter = ord(x) - key
        if new_letter > z_ascii:
            new_letter = new_letter - 26
        if new_letter < a_ascii:
            new_letter = new_letter + 26
        plaintext = plaintext + chr(new_letter)
    return plaintext

"""
def main():
    a = encrypt(-1, "BASE")
    print(a)
    print(decrypt(-1, a))


if __name__ == '__main__':
    main()
"""