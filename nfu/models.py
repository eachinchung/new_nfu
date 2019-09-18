from nfu.extensions import db


# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    password = db.Column(db.String(50))
    dormitory = db.Column(db.String(50))
    dormitory_id = db.Column(db.Integer)
    ticket_session = db.Column(db.String(50))


