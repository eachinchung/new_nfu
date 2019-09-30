from datetime import datetime

from flask import Blueprint, request, jsonify

from nfu.electric import get_electric_data
from nfu.extensions import db
from nfu.models import User, Electric
from nfu.token import validate_token

electric_bp = Blueprint('electric', __name__)


# 获取宿舍电费
@electric_bp.route('/get_electric', methods=['POST'])
def get_electric() -> str:
    token = request.form.get('access_token')
    validate = validate_token(token)

    # 验证 token 是否通过
    if validate[0]:
        user = User.query.get(validate[1]['id'])

        if user is None:
            return jsonify({'message': '该账号不存在'})

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

    else:
        # 返回验证 token 的错误
        return jsonify({'message': validate[1]})
