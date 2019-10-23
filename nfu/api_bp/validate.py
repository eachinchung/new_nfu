from flask import Blueprint, jsonify

from nfu.NFUError import NFUError
from nfu.extensions import db
from nfu.models import Power
from nfu.expand.token import validate_token

validate_bp = Blueprint('validate', __name__)


@validate_bp.route('/email/<string:token>')
def email(token: str):
    """
    验证邮箱合法性，并激活账号
    因为有账号才能拿到token，故不考虑，账号不存在的情况
    :param token: 激活邮箱的token
    :return: json
    """
    try:
        validate = validate_token(token, 'EMAIL_TOKEN')
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    # 获取用户权限表
    # 验证邮箱是否激活
    user_power = Power.query.get(validate['id'])
    if user_power.validate_email:
        return jsonify({'adopt': False, 'message': '该账号已激活'})

    user_power.validate_email = True
    db.session.add(user_power)
    db.session.commit()
    return jsonify({'adopt': True, 'message': 'success'})
