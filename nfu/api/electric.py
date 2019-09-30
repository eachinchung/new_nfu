from datetime import datetime

from flask import Blueprint, request, jsonify

from nfu.decorators import check_login
from nfu.electric import get_electric_data, ElectricPay
from nfu.extensions import db
from nfu.models import Electric, Dormitory

electric_bp = Blueprint('electric', __name__)


@electric_bp.route('/get_electric', methods=['POST'])
@check_login
def get_electric(user, error) -> str:
    """
    获取宿舍电费
    :param user: @check_login 返回用户的数据
    :param error: @check_login 返回的错误
    :return: json
    """

    if user is None:
        return jsonify({'message': error})

    electric_data = Electric.query.filter_by(room_id=user.room_id).first()

    # 当数据库没有电费数据时，我们向安心付请求数据
    if electric_data is None:
        electric = get_electric_data(user.room_id)
        if electric[0]:
            # 并将电费数据写入数据库
            electric_data = Electric(room_id=user.room_id, value=electric[1], time=datetime.now())
            db.session.add(electric_data)
            db.session.commit()
        else:
            return jsonify({'message': electric[1]})

    return jsonify({'message': 'success', 'electric': electric_data.value})


@electric_bp.route('/create_order', methods=['POST'])
@check_login
def create_order(user, error) -> str:
    """
    创建电费充值订单
    :param user: @check_login 返回用户的数据
    :param error: @check_login 返回的错误
    :return: json 跳转支付页面所必须的数据
    """

    if user is None:
        return jsonify({'message': error})

    amount = request.form.get('amount')
    dormitory = Dormitory.query.get(user.room_id)

    order = ElectricPay(amount, user.id, user.name, user.room_id, dormitory.building, dormitory.floor, dormitory.room)
    order_data = order.create_order()

    if not order_data[0]:
        return jsonify({'message': order_data[1]})

    return jsonify({'message': 'success', 'json': order_data[1], 'signature': order_data[2], 'cookies': order_data[3]})
