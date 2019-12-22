from json import loads

from flask import Blueprint, g, jsonify, request

from nfu.common import check_access_token, get_school_config
from nfu.expand.evaluating import evaluating_save, get_evaluating_teacher_course
from nfu.nfu_error import NFUError

evaluating_bp = Blueprint('evaluating', __name__)


@evaluating_bp.route('/course')
@check_access_token
@get_school_config
def get_evaluating_teacher_course_bp():
    """
    评教课程列表
    :return:
    """
    try:
        return jsonify({
            'code': '1000',
            'message': get_evaluating_teacher_course(
                g.user.id,
                g.school_config['schoolYear'],
                g.school_config['semester']
            )
        })

    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@evaluating_bp.route('/evaluating')
@check_access_token
@get_school_config
def evaluating_bp():
    """
    提交评教
    :return:
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        teacher_id = data['teacherId']
        level = data['level']
        class_name = data['className']
        teaching_class_id = data['teachingClassId']
        identification_code = data['identificationCode']
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    try:
        evaluating_save(
            g.user.id,
            g.school_config['schoolYear'],
            g.school_config['semester'],
            teacher_id=teacher_id,
            level=level,
            class_name=class_name,
            teaching_class_id=teaching_class_id,
            identification_code=identification_code
        )
        return jsonify({
            'code': '1000',
            'message': '1'
        })

    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})
