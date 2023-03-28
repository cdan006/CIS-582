from zksk import Secret, DLRep
from zksk import utils

def ZK_equality(G,H):

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    r_one = Secret(utils.get_random_num(bits=128))
    r_two = Secret(utils.get_random_num(bits=128))
    m = Secret(utils.get_random_num(bits=128))
    C1 = r_one.value * G
    C2 = m.value * G + r_one.value * H
    D1 = r_two.value * G
    D2 = m.value * G + r_two.value * H

    #Generate a NIZK proving equality of the plaintexts
    stmt = DLRep(C1, r_one * G) & DLRep(C2, r_one * H + m * G) & DLRep(D1, r_two * G) & DLRep(D2, r_two * H + m * G)
    zk_proof = stmt.prove()


    #Return two ciphertexts and the proof


    return (C1,C2), (D1,D2), zk_proof
