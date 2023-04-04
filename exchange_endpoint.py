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
import sys

from models import Base, Order, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)


@app.before_request
def create_session():
    g.session = scoped_session(DBSession)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """


def check_sig(payload, sig):
    pass


def fill_order(order): #, txes=[]):
    new_order = Order(
        buy_currency=order['buy_currency'],
        sell_currency=order['sell_currency'],
        buy_amount=order['buy_amount'],
        sell_amount=order['sell_amount'],
        sender_pk=order['sender_pk'],
        receiver_pk=order['receiver_pk']
    )


    g.session.add(new_order)
    g.session.commit()

    orders_iterate = g.session.query(Order).filter(
        Order.filled.is_(None),
        Order.buy_currency == new_order.sell_currency,
        Order.sell_currency == new_order.buy_currency,
        ((Order.sell_amount / Order.buy_amount) >= (new_order.buy_amount / new_order.sell_amount)),
        ((Order.sell_amount * new_order.sell_amount) >= (Order.buy_amount * new_order.buy_amount)),
    ).all()

    for existing_order in orders_iterate:
        if existing_order.filled is not None or new_order.filled is not None:
            continue

        time = datetime.now()
        new_order.filled = time
        existing_order.filled = time

        new_order.counterparty_id = existing_order.id
        existing_order.counterparty_id = new_order.id

        g.session.commit()

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

            g.session.add(child_order_obj)
            g.session.commit()


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
            g.session.add(child_order_obj)
            g.session.commit()

            break

    pass


def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    log_entry = Log(message=json.dumps(d))
    g.session.add(log_entry)
    g.session.commit()

    pass


def is_signature_valid(payload, sig, platform):
    if platform == 'Algorand':
        alg_encoded_msg = json.dumps(payload).encode('utf-8')
        verify = (algosdk.util.verify_bytes(alg_encoded_msg, sig, payload['sender_pk']))
        return verify
    elif platform == 'Ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
        signer_pk = eth_account.Account.recover_message(eth_encoded_msg, signature=sig)
        verify = (signer_pk == payload['sender_pk'])
        return verify
    else:
        verify = False
        return verify


""" End of helper methods """


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print(f"content = {json.dumps(content)}")
        columns = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform"]
        fields = ["sig", "payload"]

        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        # Your code here
        # Note that you can access the database session using g.session
        content = request.get_json(silent=True)
        payload = content['payload']
        sig = content['sig']
        platform = payload['platform']
        valid_signature = is_signature_valid(payload, sig, platform)
        if valid_signature == True:
            new_order = Order(
                sender_pk=payload['sender_pk'],
                receiver_pk=payload['receiver_pk'],
                buy_currency=payload['buy_currency'],
                sell_currency=payload['sell_currency'],
                buy_amount=payload['buy_amount'],
                sell_amount=payload['sell_amount'],
                signature=sig
            )
            g.session.add(new_order)
            g.session.commit()
            result = jsonify(True)
            return result
        else:
            log_message(payload)
            result = jsonify(False)
            return result
        # TODO: Check the signature

        # TODO: Add the order to the database

        # TODO: Fill the order

        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful


@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session
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
        }
        result['data'].append(order_data)

    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')