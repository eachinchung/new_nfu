from flask import Flask, jsonify

from nfu.api.electric import electric_bp
from nfu.api.oauth import oauth_bp
from nfu.api.validate import validate_bp
from nfu.extensions import db, mail, cors


# 加载基本配置
def create_app():
    app = Flask('nfu')
    app.config.from_pyfile('settings.py')

    register_blueprints(app)
    register_extensions(app)
    register_errors(app)
    return app


# 加载蓝本
def register_blueprints(app) -> None:
    app.register_blueprint(electric_bp, url_prefix='/electric')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(validate_bp, url_prefix='/validate')


# 初始化拓展
def register_extensions(app) -> None:
    cors.init_app(app)
    db.init_app(app)
    mail.init_app(app)


# 加载错误页
def register_errors(app) -> None:
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'message': '404 找不到此资源'}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'message': '500 服务器内部错误'}), 500
