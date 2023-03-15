from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False

@app.route('/verify', methods=['GET','POST'])
def verify():
    content = request.get_json(silent=True)

    #Check if signature is valid

    payload = content['payload']
    platform = payload['platform']
    pk = payload['pk']
    sig = content['sig']



    result = False
    if platform.lower() == 'ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
        if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk:
            result= jsonify(True)
        else:
            result= jsonify(False)
    elif platform.lower() == 'algorand':
        if algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, pk):
            result= jsonify(True)
        else:
            result= jsonify(False)

    return result

if __name__ == '__main__':
    app.run(port='5002')
