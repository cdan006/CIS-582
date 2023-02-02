import requests
import json

endpoint = 'https://ipfs.infura.io:5001/api/v0/'
def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    # YOUR CODE HERE

    files = {
    'file': json.dumps(data)
    }
    cid = requests.post(endpoint+"add", files=files, auth=('2L9vlTevJDocIJl8kg0wtVXJTC7','ad15ab9acc005b3533f99262f04a6654'))
    cid = cid.json()['Hash']
    return cid


def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    params = {
        'arg': cid
    }
    data = requests.post(endpoint+"cat", params=params,auth=('2L9vlTevJDocIJl8kg0wtVXJTC7', 'ad15ab9acc005b3533f99262f04a6654'))

    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    return data
"""




"""




