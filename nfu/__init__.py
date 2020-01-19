"""
    :author: Eachin Chung (钟予乾)
    :url: https://www.eachin-life.com
    :copyright: © 2020 Eachin Chung
    :license: MIT, see LICENSE for more details.
"""
from flask import Flask, jsonify

from nfu.api_bp.achievement import achievement_bp
from nfu.api_bp.class_schedule import class_schedule_bp
from nfu.api_bp.electric import electric_bp
from nfu.api_bp.oauth import oauth_bp
from nfu.api_bp.school_bus import school_bus_bp
from nfu.api_bp.user import user_bp
from nfu.api_bp.validate import validate_bp
from nfu.extensions import db, mail


def create_app(config_name=None) -> Flask:
    """
    加载基本配置
    :return:
    """
    app = Flask('nfu')
    app.config.from_pyfile('settings.py')

    # 本地开发由 flask-cors 提供 CORS
    if config_name is None:
        from flask_cors import CORS
        CORS(app)

    register_blueprints(app)
    register_extensions(app)
    register_errors(app)
    return app


def register_blueprints(app) -> None:
    """
    加载蓝本
    :param app:
    :return:
    """
    app.register_blueprint(achievement_bp, url_prefix='/achievement')
    app.register_blueprint(class_schedule_bp, url_prefix='/class-schedule')
    app.register_blueprint(electric_bp, url_prefix='/electric')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(school_bus_bp, url_prefix='/school-bus-pro')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(validate_bp, url_prefix='/validate')


def register_extensions(app) -> None:
    """
    初始化拓展
    :param app:
    :return:
    """
    db.init_app(app)
    mail.init_app(app)


def register_errors(app) -> None:
    """
    加载错误页
    :param app:
    :return:
    """

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'message': '404 错误 – 找不到此资源'}), 404

    @app.errorhandler(405)
    def page_not_found(e):
        return jsonify({'message': '405 错误 – 方法不被允许'}), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'message': '500 错误 – 服务器内部错误'}), 500
