from nfu.expand.nfu import get_jw_token, get_total_achievement_point
from nfu.extensions import db
from nfu.models import TotalAchievements


def db_init_total(user_id: int) -> dict:
    """
    向教务系统请求数据并写入数据库
    :param user_id:
    :return:
    """
    data = __get(user_id)
    return __db_input(user_id, data)


def db_update_total(user_id: int) -> dict:
    """
    更新数据库的数据
    :param user_id:
    :return:
    """
    # 向教务系统请求数据
    data = __get(user_id)

    # 删除数据库中已有的数据
    db.session.delete(TotalAchievements.query.get(user_id))
    db.session.commit()

    return __db_input(user_id, data)


def __get(user_id: int) -> dict:
    """
    向教务系统请求数据
    :param user_id:
    :return:
    """
    return get_total_achievement_point(get_jw_token(user_id))


def __db_input(user_id: int, total_achievement) -> dict:
    """
    把数据写入数据库
    :param user_id:
    :param total_achievement:
    :return:
    """
    db.session.add(
        TotalAchievements(
            id=user_id,
            get_credit=total_achievement['get_credit'],
            selected_credit=total_achievement['selected_credit'],
            average_achievement=total_achievement['average_achievement'],
            average_achievement_point=total_achievement['average_achievement_point']
        )
    )

    db.session.commit()

    return {
        'getCredit': total_achievement['get_credit'],
        'selectedCredit': total_achievement['selected_credit'],
        'averageAchievement': total_achievement['average_achievement'],
        'averageAchievementPoint': total_achievement['average_achievement_point']
    }
