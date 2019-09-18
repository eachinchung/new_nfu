from nfu.extensions import db


# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    password = db.Column(db.String(255))
    room_id = db.Column(db.Integer)
    bus_session = db.Column(db.String(50))


