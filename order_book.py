from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def process_order(order):
    if 'creater_id' in order:
        new_order = Order(
            buy_currency=order['buy_currency'],
            sell_currency=order['sell_currency'],
            buy_amount=order['buy_amount'],
            sell_amount=order['sell_amount'],
            sender_pk=order['sender_pk'],
            receiver_pk=order['receiver_pk'],
            creater_id= order['receiver_pk']
        )
    else:
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

        session.commit()

        if new_order.sell_amount < existing_order.buy_amount:
            exchange = new_order.sell_amount / new_order.buy_amount
            left_over_buy_amount = existing_order.buy_amount - new_order.sell_amount
            left_over_sell_amount = left_over_buy_amount / exchange

            child_order = {
                'buy_currency': existing_order.buy_currency,
                'sell_currency': existing_order.sell_currency,
                'buy_amount': left_over_buy_amount,
                'sell_amount': left_over_sell_amount,
                'sender_pk': existing_order.sender_pk,
                'receiver_pk': existing_order.receiver_pk,
                'creater_id': existing_order.id
            }
            child_order_obj = Order(buy_currency=child_order['buy_currency'],
                                    sell_currency=child_order['sell_currency'],
                                    buy_amount=child_order['buy_amount'],
                                    sell_amount=child_order['sell_amount'],
                                    sender_pk=child_order['sender_pk'],
                                    receiver_pk=child_order['receiver_pk']
                                    )
            process_order(child_order)

        elif new_order.buy_amount > existing_order.sell_amount:
            exchange = existing_order.sell_amount / existing_order.buy_amount
            left_over_buy_amount = new_order.buy_amount - existing_order.sell_amount
            left_over_sell_amount = left_over_buy_amount / exchange

            child_order = {
                'buy_currency': new_order.buy_currency,
                'sell_currency': new_order.sell_currency,
                'buy_amount': left_over_buy_amount,
                'sell_amount': left_over_sell_amount,
                'sender_pk': new_order.sender_pk,
                'receiver_pk': new_order.receiver_pk,
                'creater_id': new_order.id
            }
            child_order_obj = Order(buy_currency=child_order['buy_currency'],
                                    sell_currency=child_order['sell_currency'],
                                    buy_amount=child_order['buy_amount'],
                                    sell_amount=child_order['sell_amount'],
                                    sender_pk=child_order['sender_pk'],
                                    receiver_pk=child_order['receiver_pk']
                                    )
            process_order(child_order)
            break
