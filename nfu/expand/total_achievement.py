from nfu.expand.nfu import get_jw_token, get_total_achievement_point
from nfu.extensions import db
from nfu.models import TotalAchievements


def db_init_total(user_id: int) -> dict:
    """
    向教务系统请求数据并写入数据库
    :param user_id:
    :return:
    """
    total_achievement_data = get_total_achievement_point(get_jw_token(user_id))

    db.session.add(TotalAchievements(
        user_id=user_id,
        get_credit=total_achievement_data['get_credit'],
        selected_credit=total_achievement_data['selected_credit'],
        average_achievement=total_achievement_data['average_achievement'],
        average_achievement_point=total_achievement_data['average_achievement_point']
    ))

    db.session.commit()

    return {
        'getCredit': total_achievement_data['get_credit'],
        'selectedCredit': total_achievement_data['selected_credit'],
        'averageAchievement': total_achievement_data['average_achievement'],
        'averageAchievementPoint': total_achievement_data['average_achievement_point']
    }


def db_update_total(user_id: int) -> dict:
    """
    更新数据库的数据
    :param user_id:
    :return:
    """
    total_achievement_data = get_total_achievement_point(get_jw_token(user_id))

    achievement_db = TotalAchievements.query.get(user_id)
    achievement_db.get_credit = total_achievement_data['get_credit']
    achievement_db.selected_credit = total_achievement_data['selected_credit']
    achievement_db.average_achievement = total_achievement_data['average_achievement']
    achievement_db.average_achievement_point = total_achievement_data['average_achievement_point']

    db.session.add(achievement_db)
    db.session.commit()

    return {
        'getCredit': total_achievement_data['get_credit'],
        'selectedCredit': total_achievement_data['selected_credit'],
        'averageAchievement': total_achievement_data['average_achievement'],
        'averageAchievementPoint': total_achievement_data['average_achievement_point']
    }
