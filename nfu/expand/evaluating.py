from json import decoder, loads

from requests import post

from nfu.nfu_error import NFUError


def get_evaluating_teacher_course(token: str, school_year: int, semester: int) -> list:
    """
    获取待评教课程
    :param token:
    :param school_year:
    :param semester:
    :return:
    """
    url = 'http://ecampus.nfu.edu.cn:2929/jw-amsi/amsEvalTeacher/r-getEvaluatingTeacherCourse'
    data = {
        'deleted': False,
        'pageSize': 20,
        'xn': school_year,
        'xq': semester,
        'checkType': 0,
        'jwloginToken': token
    }

    try:
        response = post(url, data=data, timeout=10)
        data = loads(response.text)['msg']['list']
    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

    return data


def evaluating_save(token: str, school_year: int, semester: int, *, teacher_id: int, level: int, class_name: str,
                    teaching_class_id: int, identification_code: str):
    """
    评教
    :param token:
    :param teacher_id:
    :param level:
    :param class_name:
    :param teaching_class_id:
    :param identification_code:
    :param school_year:
    :param semester:
    :return:
    """
    url = 'http://ecampus.nfu.edu.cn:2929/jw-amsi/amsEvalTeacher/r-getEvaluatingTargetList'
    data = {
        'deleted': False,
        'pageSize': 65535,
        'kczkhfsdm': identification_code,
        'jwloginToken': token
    }

    try:
        response = post(url, data=data, timeout=10)
        target_list = loads(response.text)['msg']['list']
    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

    url = 'http://ecampus.nfu.edu.cn:2929/jw-amsi/amsEvalTeacher/w-saveAll'

    data = []
    for target in target_list:
        data.append({
            'xn': school_year,
            'xq': semester,
            'targetId': target['id'],
            'jxbId': teaching_class_id,
            'yjkcMc': class_name,
            "teacherId": teacher_id,
            "content": target["content"],
            "kczkhfsdm": target["kczkhfsdm"],
            "levelId": level
        })

    try:
        post(url, data=data, timeout=10)
    except OSError:
        raise NFUError('教务系统错误，请稍后再试')
