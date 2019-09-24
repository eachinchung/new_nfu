from flask import Blueprint, jsonify

from nfu.extensions import db
from nfu.models import User
from nfu.token import validate_token

validate_bp = Blueprint('validate', __name__)


# 验证邮箱合法性，并激活账号
@validate_bp.route('/email/<string:token>')
def email(token) -> jsonify:
    validate = validate_token(token, 'EMAIL_TOKEN')
    if validate[0]:
        user = User.query.get(validate[1]['user_id'])
        if user is not None and not user.validate_email:
            user.validate_email = True
            db.session.add(user)
            db.session.commit()
            return jsonify({'message': 'success'})
        else:
            return jsonify({'message': '该账号已激活'})
    else:
        return jsonify({'message': validate[1]})
