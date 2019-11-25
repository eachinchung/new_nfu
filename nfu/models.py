from json import loads

from werkzeug.security import check_password_hash

from nfu.extensions import db


# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    room_id = db.Column(db.Integer)
    email = db.Column(db.String)
    bus_session = db.Column(db.String)

    def validate_password(self, password):
        return check_password_hash(self.password, password)


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

    def get_dict(self):
        return {
            'getCredit': self.get_credit,
            'selectedCredit ': self.selected_credit,
            'averageAchievement ': self.average_achievement,
            'averageAchievement_point': self.average_achievement_point
        }


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
    resit_exam_achievement_point = db.Column(db.Float)

    def get_dict(self):
        return {
            'schoolYear': self.school_year,
            'semester': self.semester,
            'courseType': self.course_type,
            'courseName': self.course_name,
            'courseId': self.course_id,
            'resitExam': self.resit_exam,
            'credit': self.credit,
            'achievementPoint': self.achievement_point,
            'finalAchievements': self.final_achievements,
            'totalAchievements': self.total_achievements,
            'midtermAchievements': self.midterm_achievements,
            'practiceAchievements': self.practice_achievements,
            'peacetimeAchievements': self.peacetime_achievements,
            'resitExamAchievementPoint': self.resit_exam_achievement_point
        }


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
            'courseName': self.course_name,
            'courseId': self.course_id,
            'teacher': loads(self.teacher),
            'classroom': self.classroom,
            'weekday': self.weekday,
            'startNode': self.start_node,
            'endNode': self.end_node,
            'startWeek': self.start_week,
            'endWeek': self.end_week
        }


# 车票订单
class TicketOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    bus_ids = db.Column(db.Integer)
    passenger_ids = db.Column(db.String)
    order_type = db.Column(db.Integer)
    order_time = db.Column(db.DateTime)
    order_state = db.Column(db.Integer)
    ticket_time = db.Column(db.DateTime)
