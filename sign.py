from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair

from fastecdsa import curve, ecdsa, keys, point
from hashlib import sha256

def sign(m):
	#generate public key
	#Your code here
	private_key = keys.gen_private_key(curve.P256)
	public_key = keys.get_public_key(private_key, curve.P256)
	#generate signature
	#Your code here
	r = 0
	s = 0
	r, s = ecdsa.sign(m, public_key)

	assert isinstance( public_key, point.Point )
	assert isinstance( r, int )
	assert isinstance( s, int )
	return( public_key, [r,s] )


