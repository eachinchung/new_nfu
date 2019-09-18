"""
    :author: Eachin
    :url: https://www.eachin-life.com
    :copyright: © 2019 Eachin Chung <EachinChung@gmail.com>
"""
from flask import Flask

from nfu.extensions import db


# 加载基本配置
def create_app(config_name=None):
    app = Flask('nfu')
    app.config.from_pyfile('settings.py')
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    register_extensions(app)
    return app


# 初始化拓展
def register_extensions(app):
    db.init_app(app)
