from werkzeug.security import generate_password_hash, check_password_hash

from nfu.extensions import db


# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    password = db.Column(db.String(94))
    room_id = db.Column(db.Integer)
    email = db.Column(db.String(255))
    bus_session = db.Column(db.String(50))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password, password)


# 权限表
class Power(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    validate_email = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)


# 电费表
class Electric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, index=True)
    value = db.Column(db.Float)
    time = db.Column(db.Date)
