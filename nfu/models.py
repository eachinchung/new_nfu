from werkzeug.security import check_password_hash, generate_password_hash

from nfu.extensions import db


# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    room_id = db.Column(db.Integer)
    email = db.Column(db.String)
    bus_session = db.Column(db.String)

    # 出于用户隐私保护，用户密码我们将采用哈希加密
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password, password)


# 权限表
class Power(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    validate_email = db.Column(db.Boolean, default=False)
    school_bus = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)

    # 返回权限字典
    def get_dict(self):
        return {
            'id': self.id,
            'validate_email': self.validate_email,
            'school_bus': self.school_bus,
            'admin': self.admin
        }


# 宿舍表
class Dormitory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String)
    floor = db.Column(db.String)
    room = db.Column(db.Integer)


# 电费表
class Electric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, index=True)
    value = db.Column(db.Float)
    time = db.Column(db.Date)


# 总成绩表
class TotalAchievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    get_credit = db.Column(db.Integer)
    selected_credit = db.Column(db.Integer)
    average_achievement = db.Column(db.Float)
    average_achievement_point = db.Column(db.Float)


# 成绩表
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    school_year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    course_type = db.Column(db.String)
    course_name = db.Column(db.String)
    course_id = db.Column(db.String)
    resit_exam = db.Column(db.Boolean)
    credit = db.Column(db.Float)
    achievement_point = db.Column(db.Float)
    final_achievements = db.Column(db.Float)
    total_achievements = db.Column(db.Float)
    midterm_achievements = db.Column(db.Float)
    practice_achievements = db.Column(db.Float)
    peacetime_achievements = db.Column(db.Float)


# 课程表
class ClassSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    school_year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    course_name = db.Column(db.String)
    course_id = db.Column(db.String)
    teacher = db.Column(db.String)
    classroom = db.Column(db.String)
    weekday = db.Column(db.Integer)
    start_node = db.Column(db.Integer)
    end_node = db.Column(db.Integer)
    start_week = db.Column(db.Integer)
    end_week = db.Column(db.Integer)

    def get_dict(self):
        return {
            'course_name': self.course_name,
            'teacher': self.teacher,
            'classroom': self.classroom,
            'weekday': self.weekday,
            'start_node': self.start_node,
            'end_node': self.end_node,
            'start_week': self.start_week,
            'end_week': self.end_week
        }


# 车票订单
class TicketOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    ticket_time = db.Column(db.DateTime)
    bus_ids = db.Column(db.String)
    passenger_ids = db.Column(db.String)
    order_message = db.Column(db.String)
    order_time = db.Column(db.DateTime)
    trade_no = db.Column(db.String)
