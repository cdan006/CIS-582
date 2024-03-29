from sqlalchemy import null
from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.toChecksumAddress(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
#with open('abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://eth-mainnet.alchemyapi.io/v2/GLLQaGD5qcQBE4pYw99EZz37c3X1FfOf"# YOU WILL NEED TO TO PROVIDE THE URL OF AN ETHEREUM NODE. bdnodes.net
provider = HTTPProvider(api_url)
web3 = Web3(provider)
cid = "QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/1"
gateway = {'infura': "https://ipfs.infura.io:5001/api/v0/cat?arg=", 'pinata': "https://gateway.pinata.cloud/ipfs/", 'ipfs': "https://ipfs.io/ipfs/"}

def get_ape_info(apeID):
    assert isinstance(apeID, int), f"{apeID} is not an int"
    assert 1 <= apeID, f"{apeID} must be at least 1"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE
    contract = web3.eth.contract(address=contract_address, abi=abi)
    data['owner'] = contract.functions.ownerOf(apeID).call()
    token_uri = contract.functions.tokenURI(apeID).call()
    token = token_uri.replace('ipfs://', '')
    for x, y in gateway.items():
        if x != 'infura':
            response = requests.get(y+token)
        else:
            response = requests.post(y+token)

        if response.status_code == 200:
            metadata = response.json()
            data['image'] = metadata['image']
            attributes = metadata['attributes']
            for a in attributes:
                if a['trait_type'].lower() == 'eyes':
                    data['eyes'] = a['value']
                    break


    assert isinstance(data, dict), f'get_ape_info{apeID} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data
"""
if __name__ == "__main__":
    data = get_ape_info(20)
    print(data)"""