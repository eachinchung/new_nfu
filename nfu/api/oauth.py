from flask import Blueprint, request, jsonify

from nfu.expand import generate_token
from nfu.models import User

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/get_token', methods=['POST'])
def get_token():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.get(username)
    if user is None or not user.validate_password(password):
        return jsonify({'message': '账号或密码错误'})

    return jsonify({
        'message': 'success',
        'access_token': generate_token({'id': user.id}),
        'refresh_token': generate_token({'id': user.id}, token_type='REFRESH_TOKEN', expires_in=172800)
    })


@oauth_bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    pass
