from flask import Flask
from flask_cors import CORS

from nfu.api.oauth import oauth_bp
from nfu.extensions import db


# 加载基本配置
def create_app(config_name=None):
    app = Flask('nfu')
    app.config.from_pyfile('settings.py')
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    register_blueprints(app)
    register_extensions(app)
    return app


# 加载蓝本
def register_blueprints(app):
    app.register_blueprint(oauth_bp, url_prefix='/oauth')


# 初始化拓展
def register_extensions(app):
    CORS(app)
    db.init_app(app)
