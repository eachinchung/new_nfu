from flask import Blueprint, request, jsonify

from nfu.expand import generate_token
from nfu.models import User

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/token/get', methods=['POST'])
def get_token():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.get(username)
    if user is None or not user.validate_password(password):
        return jsonify({'message': '账号或密码错误'})

    token, remember_token = generate_token(user)

    return jsonify({
        'message': 'success',
        'token': token,
        'remember_token': remember_token,
    })
