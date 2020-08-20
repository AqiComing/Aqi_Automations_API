from api_test.common import code
from api_test.common.api_response import JsonResponse


def parameter_id_check(data):
    """
    检查传入项目id或者id列表参数可用性
    :param data:
    :return:
    """
    try:
        if not isinstance(data['ids'], list) or not isinstance(data['project_id'], int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        for i in data['ids']:
            if not isinstance(i, int):
                return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)
