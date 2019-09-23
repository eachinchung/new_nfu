from flask import Flask

from nfu.api.oauth import oauth_bp
from nfu.extensions import db, mail, cors


# 加载基本配置
def create_app():
    app = Flask('nfu')
    app.config.from_pyfile('settings.py')

    register_blueprints(app)
    register_extensions(app)
    return app


# 加载蓝本
def register_blueprints(app):
    app.register_blueprint(oauth_bp, url_prefix='/oauth')


# 初始化拓展
def register_extensions(app):
    cors.init_app(app)
    db.init_app(app)
    mail.init_app(app)
