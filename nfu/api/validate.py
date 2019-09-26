from flask import Blueprint, jsonify

from nfu.extensions import db
from nfu.models import Power
from nfu.token import validate_token

validate_bp = Blueprint('validate', __name__)


# 验证邮箱合法性，并激活账号
@validate_bp.route('/email/<string:token>')
def email(token) -> str:
    validate = validate_token(token, 'EMAIL_TOKEN')
    # 验证token是否通过
    if validate[0]:
        user_power = Power.query.get(validate[1]['user_id'])
        # 验证邮箱是否激活
        # 因不存在账号几乎不可能获取token，
        # 故合并两个验证。
        if user_power is not None and not user_power.validate_email:
            user_power.validate_email = True
            db.session.add(user_power)
            db.session.commit()
            return jsonify({'message': 'success'})
        else:
            return jsonify({'message': '该账号已激活'})
    else:
        return jsonify({'message': validate[1]})
