"""
    :author: Eachin
    :url: https://www.eachin-life.com
    :copyright: © 2019 Eachin Chung <EachinChung@gmail.com>
"""
import os

SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
