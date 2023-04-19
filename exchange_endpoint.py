from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import math
import sys
import traceback
from web3 import Web3
from eth_account import Account

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

""" Pre-defined methods (do not need to change) """


@app.before_request
def create_session():
    g.session = scoped_session(DBSession)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


def connect_to_blockchains():
    try:
        # If g.acl has not been defined yet, then trying to query it fails
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True

    try:
        if acl_flag or not g.acl.status():
            # Define Algorand client for the application
            g.acl = connect_to_algo()
    except Exception as e:
        print("Trying to connect to algorand client again")
        print(traceback.format_exc())
        g.acl = connect_to_algo()

    try:
        icl_flag = False
        g.icl
    except AttributeError as ae:
        icl_flag = True

    try:
        if icl_flag or not g.icl.health():
            # Define the index client
            g.icl = connect_to_algo(connection_type='indexer')
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type='indexer')

    try:
        w3_flag = False
        g.w3
    except AttributeError as ae:
        w3_flag = True

    try:
        if w3_flag or not g.w3.isConnected():
            g.w3 = connect_to_eth()
    except Exception as e:
        print("Trying to connect to web3 again")
        print(traceback.format_exc())
        g.w3 = connect_to_eth()


""" End of pre-defined methods """

""" Helper Methods (skeleton code for you to implement) """


def log_message(message_dict):
    #msg = json.dumps(message_dict)

    # TODO: Add message to the Log table
    log_entry = Log(message=json.dumps(message_dict))
    g.session.add(log_entry)
    g.session.commit()

    return




def is_signature_valid(payload, sig, platform):
    if platform == 'Algorand':
        alg_encoded_msg = json.dumps(payload).encode('utf-8')
        verify = (algosdk.util.verify_bytes(alg_encoded_msg, sig, payload['sender_pk']))
        return verify
    elif platform == 'Ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
        signer_pk = eth_account.Account.recover_message(eth_encoded_msg, signature=sig)
        verify = (signer_pk.lower() == payload['sender_pk'].lower())
        return verify
    else:
        verify = False
        return verify


def get_algo_keys():
    mnemonic_secret = "original crisp season bike anchor live punch survey reject egg wink moon obvious paddle hazard engage elephant chunk panther violin daughter hen genre ability alarm"
    algo_sk= algosdk.mnemonic.to_private_key(mnemonic_secret)
    algo_pk = algosdk.mnemonic.to_public_key(mnemonic_secret)

    return algo_sk, algo_pk
def get_eth_keys(filename="eth_mnemonic.txt"):
    w3 = Web3()

    # TODO: Generate or read (using the mnemonic secret)
    # the ethereum public/private keys
    #with open(filename, "r") as f:
    #    mnemonic_secret = f.read().strip()

    #mnemonic_secret = 'garden faint wink child monster remove mirror advice choice screen luxury monkey'
    w3.eth.account.enable_unaudited_hdwallet_features()
    acct, mnemonic_secret = w3.eth.account.create_with_mnemonic()
    acct = w3.eth.account.from_mnemonic(mnemonic_secret)
    eth_pk = acct._address
    eth_sk = acct._private_key
    return eth_sk, eth_pk

def fill_order(order, txes=[]):
    # TODO:
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!
    new_order = Order(
        buy_currency=order['buy_currency'],
        sell_currency=order['sell_currency'],
        buy_amount=order['buy_amount'],
        sell_amount=order['sell_amount'],
        sender_pk=order['sender_pk'],
        receiver_pk=order['receiver_pk']
    )

    print("1")
    print("new_order buy_currency",new_order.buy_currency)
    print("new_order sell_currency", new_order.sell_currency)
    print("new_order sell_amount", new_order.sell_amount)
    print("new_order buy_amount", new_order.buy_amount)

    g.session.add(new_order)
    g.session.commit()
    """
    orders_iterate = g.session.query(Order).filter(
        Order.filled.is_(None),
        Order.buy_currency == new_order.buy_currency,
        Order.sell_currency == new_order.sell_currency,
        Order.sell_amount == new_order.sell_amount,
        Order.buy_amount == new_order.buy_amount
    ).all()

    """

    orders_iterate_all = g.session.query(Order).filter(
    ).all()
    e = 1
    for ord in orders_iterate_all:
        print("ord type", type(ord))
        print("Order.buy_currency", ord.buy_currency)
        print("Order.sell_currency", ord.sell_currency)
        print("Order.sell_amount", ord.sell_amount)
        print("Order.buy_amount", ord.buy_amount)
        e += 1

    orders_iterate = g.session.query(Order).filter(
        Order.filled.is_(None),
        Order.buy_currency == new_order.sell_currency,
        Order.sell_currency == new_order.buy_currency,
        ((Order.sell_amount / Order.buy_amount) >= (new_order.buy_amount / new_order.sell_amount)),
        ((Order.sell_amount * new_order.sell_amount) >= (Order.buy_amount * new_order.buy_amount)),
    ).all()
    print("orders_iterate", orders_iterate)



    for existing_order in orders_iterate:
        print("existing_order", existing_order)
        if existing_order.filled is not None or new_order.filled is not None:
            continue

        time = datetime.now()
        new_order.filled = time
        existing_order.filled = time

        new_order.counterparty_id = existing_order.id
        existing_order.counterparty_id = new_order.id

        g.session.commit()
        print("A")
        print("new_order.sell_amount", new_order.sell_amount)
        print("existing_order.buy_amount", existing_order.buy_amount)
        print("new_order.buy_amount", new_order.buy_amount)
        print("existing_order.sell_amount", existing_order.sell_amount)

        if new_order.sell_amount < existing_order.buy_amount:
            left_over_buy_amount = existing_order.buy_amount - new_order.sell_amount
            left_over_sell_amount = left_over_buy_amount * (existing_order.sell_amount / existing_order.buy_amount)

            child_order = {
                'buy_currency': existing_order.buy_currency,
                'sell_currency': existing_order.sell_currency,
                'buy_amount': left_over_buy_amount,
                'sell_amount': left_over_sell_amount,
                'sender_pk': existing_order.sender_pk,
                'receiver_pk': existing_order.receiver_pk,
                'creator_id': existing_order.id
            }
            child_order_obj = Order(buy_currency=child_order['buy_currency'],
                                    sell_currency=child_order['sell_currency'],
                                    buy_amount=child_order['buy_amount'],
                                    sell_amount=child_order['sell_amount'],
                                    sender_pk=child_order['sender_pk'],
                                    receiver_pk=child_order['receiver_pk'],
                                    creator_id=child_order['creator_id']
                                    )
            print("3")
            g.session.add(child_order_obj)
            g.session.commit()
            print("3a")
        elif new_order.buy_amount > existing_order.sell_amount:
            left_over_buy_amount = new_order.buy_amount - existing_order.sell_amount
            left_over_sell_amount = left_over_buy_amount * (new_order.sell_amount / new_order.buy_amount)

            child_order = {
                'buy_currency': new_order.buy_currency,
                'sell_currency': new_order.sell_currency,
                'buy_amount': left_over_buy_amount,
                'sell_amount': left_over_sell_amount,
                'sender_pk': new_order.sender_pk,
                'receiver_pk': new_order.receiver_pk,
                'creator_id': new_order.id

            }
            child_order_obj = Order(buy_currency=child_order['buy_currency'],
                                    sell_currency=child_order['sell_currency'],
                                    buy_amount=child_order['buy_amount'],
                                    sell_amount=child_order['sell_amount'],
                                    sender_pk=child_order['sender_pk'],
                                    receiver_pk=child_order['receiver_pk'],
                                    creator_id = child_order['creator_id']
                                    )
            print("4")
            g.session.add(child_order_obj)
            g.session.commit()
            print("5")
            break
    if new_order.filled is not None:
        print("6")
        g.session.add(new_order)
        g.session.commit()
        print("7")
        txes.append(new_order)
        txes.append(existing_order)
        execute_txes(txes)
        print("8")
    for tx in txes:
        fill_order(tx)
    pass


def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print("txes: ", txes)
    print(f"Trying to execute {len(txes)} transactions")
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()

    print("1234")
    """
    if not all(tx['platform'] in ["Algorand", "Ethereum"] for tx in txes):
        print("Error: execute_txes got an invalid platform!")
        print(tx['platform'] for tx in txes)
        """
    print("12345")
    #algo_txes = [tx for tx in txes if tx['platform'] == "Algorand"]
    #eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum"]

    # TODO:
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens_old.py
    #       2. Add all transactions to the TX table

    for tx in txes:
        print("12346")
        print("tx senderpk", tx['sender_pk'])
        if tx['sender_pk'] == algo_pk:
            result = send_tokens_algo(algo_sk, tx.receiver_pk, tx.sell_amount)
            print("AB")
            if result == True:
                new_tx = TX(
                    platform=tx.platform,
                    receiver_pk=tx.receiver_pk,
                    order_id=tx.order_id,
                    tx_id=tx.id
                )

                g.session.add(new_tx)
                g.session.commit()
            else:
                print(f"Failed to execute transaction for order {tx.id}")
        elif tx['sender_pk'] == eth_pk:
            result = send_tokens_eth(g.w3, eth_sk, tx)
            print("AC")
            if result == True:
                new_tx = TX(
                    platform=tx.platform,
                    receiver_pk=tx.receiver_pk,
                    order_id=tx.order_id,
                    tx_id=tx.id
                )
                g.session.add(new_tx)
                g.session.commit()

            else:
                print(f"Failed to execute transaction for order {tx.id}")

    """
    print("EA AA")
    for tx in algo_txes:
        result = send_tokens_algo(algo_sk, tx.receiver_pk, tx.sell_amount)
        print("AB")
        if result==True:
            new_tx = TX(
                platform=tx.platform,
                receiver_pk=tx.receiver_pk,
                order_id=tx.order_id,
                tx_id=tx.id
            )

            g.session.add(new_tx)
            g.session.commit()
        else:
            print(f"Failed to execute transaction for order {tx.id}")
    for tx in eth_txes:
        result = send_tokens_eth(g.w3, eth_sk, tx)
        print("AC")
        if result==True:
            new_tx = TX(
                platform=tx.platform,
                receiver_pk=tx.receiver_pk,
                order_id=tx.order_id,
                tx_id=tx.id
            )
            g.session.add(new_tx)
            g.session.commit()

        else:
           print(f"Failed to execute transaction for order {tx.id}")
        """
    pass


""" End of Helper methods"""


@app.route('/address', methods=['POST'])
def address():
    print("Test Print", file=sys.stderr)
    if request.method == "POST":
        content = request.get_json(silent=True)
        if 'platform' not in content.keys():
            print(f"Error: no platform provided")
            return jsonify("Error: no platform provided")
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print(f"Error: {content['platform']} is an invalid platform")
            return jsonify(f"Error: invalid platform provided: {content['platform']}")

        if content['platform'] == "Ethereum":
            # Your code here'
            #eth_sk, eth_pk = get_eth_keys()
            #return jsonify({"public_key": eth_pk})

            eth_sk, eth_pk = get_eth_keys()
            return jsonify(eth_pk)
        if content['platform'] == "Algorand":
            # Your code here
            alg_sk, alg_pk = get_algo_keys()
            return jsonify(alg_pk)
            #return jsonify({"public_key": alg_pk})


@app.route('/trade', methods=['POST'])
def trade():
    w3 = Web3()
    print("In trade", file=sys.stderr)
    print("In trade test")
    connect_to_blockchains()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = ["buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
        fields = ["sig", "payload"]
        error = False
        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)
        content = request.get_json(silent=True)
        payload = content['payload']
        sig = content['sig']
        platform = payload['platform']
        if platform == "Algorand":
            algo_sk, algo_pk = get_algo_keys()
        elif platform == "Ethereum":
            eth_sk, eth_pk = get_eth_keys()
        valid_signature = is_signature_valid(payload, sig, platform)
        if valid_signature == True:
            new_order = Order(
                sender_pk=algo_pk if platform == "Algorand" else eth_pk,
                receiver_pk=payload['receiver_pk'],
                buy_currency=payload['buy_currency'],
                sell_currency=payload['sell_currency'],
                buy_amount=payload['buy_amount'],
                sell_amount=payload['sell_amount'],
                tx_id = payload['tx_id']

            )
            print("no buy_current", new_order.buy_currency)
            print("no sell_current", new_order.sell_currency)
            print("no buy amaount", new_order.buy_amount)
            print("no sell amount", new_order.sell_amount)
            equal_sell_amount = False
            print("platform", platform)
            if platform == "Algorand":
                transactions = g.icl.search_transactions(txid=new_order.tx_id)
                print(transactions)
                transaction_amount = transactions['transactions'][0]['payment-transaction']['amount']
                if transaction_amount >= new_order.sell_amount:
                    equal_sell_amount = True
                    print("equal_sell_amount", equal_sell_amount)
            elif platform == "Ethereum":
                print("E")
                transactions = g.w3.eth.get_transaction(new_order.tx_id) #why is this wrong?
                print("Ethereum transactions", transactions)
                if transactions['value'] >= new_order.sell_amount:
                    equal_sell_amount = True
            if equal_sell_amount == False:
                result = jsonify(False)
                print("Returning jsonify(False) due to sell amount not being equal")
                return result
            #g.session.add(new_order)
            #g.session.commit()
            print("test")
            print("new_order", new_order)
            print("new_order type", type(new_order))

            transaction_data = {
                'sender_pk': algo_pk if platform == "Algorand" else eth_pk,
                'receiver_pk': payload['receiver_pk'],
                'buy_currency': payload['buy_currency'],
                'sell_currency': payload['sell_currency'],
                'buy_amount': payload['buy_amount'],
                'sell_amount': payload['sell_amount'],
                'tx_id': payload['tx_id']
            }
            fill_order(transaction_data)
            print("test2")
            result = jsonify(True)
            print("Returning jsonify(True) as everything went well")
            return result
        else:
            log_message(payload)
            result = jsonify(False)
            print("Returning jsonify(False) due to invalid signature")
            return result

    return jsonify(True)


@app.route('/order_book')
def order_book():
    # Same as before
    print("order book")
    fields = ["buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature", "tx_id", "receiver_pk","sender_pk"]
    all_orders = g.session.query(Order).all()
    result = {'data': []}
    for o in all_orders:
        order_data = {
            'sender_pk': o.sender_pk,
            'receiver_pk': o.receiver_pk,
            'buy_currency': o.buy_currency,
            'sell_currency': o.sell_currency,
            'buy_amount': o.buy_amount,
            'sell_amount': o.sell_amount,
            'signature': o.signature,
            'tx_id': o.tx_id,

        }
        result['data'].append(order_data)

    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
