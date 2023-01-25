#from fastecdsa.curve import secp256k1
#from fastecdsa.keys import export_key, gen_keypair

#from fastecdsa import curve, ecdsa, keys, point
from fastecdsa import curve
from fastecdsa import ecdsa
from fastecdsa import keys
from fastecdsa import point
from hashlib import sha256

#use the sign and verify functions in https://fastecdsa.readthedocs.io/en/stable/fastecdsa.html
def sign(m):
	#generate public key
	#Your code here
	private_key = keys.get_private_key(curve = curve.secp256k1)
	public_key = keys.get_public_key(private_key, curve = curve.secp256k1)
	r = 0
	s = 0

	r,s = fastecdsa.ecdsa.sign(m,private_key, curve = curve.secp256k1)

	assert isinstance( public_key, point.Point )
	assert isinstance( r, int )
	assert isinstance( s, int )
	return( public_key, [r,s] )
