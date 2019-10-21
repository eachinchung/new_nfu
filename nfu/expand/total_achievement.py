from nfu.models import TotalAchievements
from nfu.expand.nfu import get_jw_token, get_total_achievement_point
from nfu.extensions import db


def db_init_total(user_id: int):
    data = __get(user_id)

    if data[0]:
        return True, __db_input(user_id, data[1])

    return False, data[1]


def db_update_total(user_id: int):
    # 向教务系统请求数据
    data = __get(user_id)
    if not data[0]:
        return False, data[1]

    # 删除数据库中已有的数据
    db.session.delete(TotalAchievements.query.get(user_id))
    db.session.commit()

    return True, __db_input(user_id, data[1])


def __get(user_id: int) -> tuple:
    try:
        token = get_jw_token(user_id)
    except LookupError as err:
        raise LookupError(str(err))

    total_achievement = get_total_achievement_point(token)
    if total_achievement[0]:
        return True, total_achievement[1]

    return False, total_achievement[1]


def __db_input(user_id: int, total_achievement) -> dict:
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
        'get_credit': total_achievement['get_credit'],
        'selected_credit ': total_achievement['selected_credit'],
        'average_achievement ': total_achievement['average_achievement'],
        'average_achievement_point': total_achievement['average_achievement_point']
    }
