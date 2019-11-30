from json import dumps
from os import getenv
from random import randint

from flask import g
from redis import Redis

from nfu.extensions import db
from nfu.models import TicketOrder


def generate_order_number(order_type: int, today):
    """
    生成订单号
    :param today:
    :param order_type:
    :return:
    """
    user_id = str(g.user.id)
    return f"{order_type}{user_id[1]}{today.strftime('%y%m%d%H%M%S')}{randint(100, 999)}{user_id[-3:]}"


def put_mysql(data: dict, order_id: str, today):
    """
    订单写入 Mysql
    :param data:
    :param order_id:
    :param today:
    :return:
    """
    order = TicketOrder()
    order.user_id = g.user.id
    order.bus_ids = data['busId']
    order.passenger_ids = dumps(data['passengerIds'])
    order.order_id = order_id
    order.order_type = data['orderType']
    order.order_time = today
    order.order_state = data['orderState']
    order.ticket_date = data['ticketDate']

    db.session.add(order)
    db.session.commit()


def put_redis(data: dict, order_id: str):
    """
    预售订单写入Redis
    :param data:
    :param order_id:
    :return:
    """
    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    if data['orderType'] == 1:
        #
        # 判断订单时间
        #
        r.hset(f'{data["ticketDate"]}_accelerate', order_id, dumps({
            'busId': data['busId'],
            'passengerIds': data['passengerIds'],
            'ticketDate': data['ticketDate'],
            'takeStation': data['takeStation'],
            'alipayUserId': g.bus_user.alipay_user_id,
            'idCard': g.bus_user.id_card
        }))

    # 刷票订单写入Redis
    if data['orderType'] == 2:
        r.hset('accelerate_order', order_id, dumps({
            'busId': data['busId'],
            'passengerIds': data['passengerIds'],
            'ticketDate': data['ticketDate'],
            'takeStation': data['takeStation'],
            'busSession': g.bus_user.bus_session
        }))
