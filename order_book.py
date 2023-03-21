from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def process_order(order):
    new_order = Order(
        buy_currency=order['buy_currency'],
        sell_currency=order['sell_currency'],
        buy_amount=order['buy_amount'],
        sell_amount=order['sell_amount'],
        sender_pk=order['sender_pk'],
        receiver_pk=order['receiver_pk']
    )
    session.add(new_order)
    session.commit()

    orders_iterate = session.query(Order).filter(
        Order.filled.is_(None),
        Order.buy_currency == new_order.sell_currency,
        Order.sell_currency == new_order.buy_currency,
        ((Order.sell_amount / Order.buy_amount) >= (new_order.buy_amount / new_order.sell_amount))
    ).all()

    for o in orders_iterate:
        if new_order.filled or o.filled:
            continue

        time = datetime.datetime.now()
        new_order.filled = time
        o.filled = time

        new_order.counterparty_id = o.id
        o.counterparty_id = new_order.id

        session.commit()

        if new_order.sell_amount > o.buy_amount:
            i_exchange = new_order.sell_amount / new_order.buy_amount
            left_over_sell_amount = new_order.sell_amount - o.buy_amount
            left_over_buy_amount = left_over_sell_amount / i_exchange

            child_order = {
                'buy_currency': new_order.buy_currency,
                'sell_currency': new_order.sell_currency,
                'buy_amount': left_over_buy_amount,
                'sell_amount': left_over_sell_amount,
                'sender_pk': new_order.sender_pk,
                'receiver_pk': new_order.receiver_pk
            }

            process_order(child_order)

            break