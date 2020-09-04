from django.core.exceptions import ObjectDoesNotExist

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.models import Project


def parameter_id_check(data):
    """
    检查 projrct id, id
    :param data:
    :return:
    """
    try:
        if not isinstance(data['project_id'],int) or not isinstance(data['id'],int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


def parameter_ids_check(data):
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


def project_status_check(request):
    """
    项目状态检查，检查get请求中的project_id对应的项目状态
    :param request:
    :return:
    """
    project_id = request.GET.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    try:
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST, msg="项目不存在或已删除！")
    if not project.status:
        return JsonResponse(code=code.CODE_PROJECT_DISABLE)
