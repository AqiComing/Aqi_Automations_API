from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import get_availability_project, record_dynamic
from api_test.models import Project, APIInfo, APIGroup, APIParameterRaw
from api_test.serializer import APIInfoSerializer, APIParameterSerializer, APIParameterRawSerializer, \
    APIResponseSerializer, APIInfoDeserializer, APIHeadSerializer


def all_parameter_check(data):
    """
    检查所有参数
    :param data:
    :return:
    """
    try:
        if not data['project_id'] or not data['name'] or not data['http_type'] or not data['request_type'] or not data[
            'api_address'] or not data['request_parameter_type'] or not data['status']:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR,msg='必需参数值未空')
        if data['status'] not in (True,False):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR,)
        if not isinstance(data['project_id'],int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        if data['http_type'] not in ('HTTP', "HTTPS") or data['request_type'] not in (
            'POST', 'GET', 'PUT', 'DELETE') or data['request_parameter_type'] not in ['form-data', 'raw', 'Restful']:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


class AddAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        新增接口
        :param request:
        :return:
        """

        data=JSONParser().parse(request)
        data['update_user'] = request.user.pk
        project=get_availability_project(data,request.user)
        result=all_parameter_check(data) if isinstance(project,Project) else project
        if result:
            return result
        same_name_api=APIInfo.objects.filter(name=data['name'],project=project.id)
        if len(same_name_api):
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME,msg='存在同名API')
        else:
            with transaction.atomic(): #执行错误后，协助事务回滚‘
                serializer=APIInfoDeserializer(data=data)
                if serializer.is_valid():
                    try:
                        if not isinstance(data.get('api_group'),int):
                            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
                        api_group=APIGroup.objects.get(id=data['api_group'],project=project.id)
                        serializer.save(project=project,api_group=api_group)
                    except KeyError:
                        serializer.save(project=project)
                    except ObjectDoesNotExist:
                        return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='分组不存在')
                    api_id=serializer.data.get('id')
                    # 保存Header
                    if len(data.get('head_dict')):
                        for head in data['head_dict']:
                            if head.get("name"):
                                head["api"]=api_id
                                serializer=APIHeadSerializer(data=head)
                                if serializer.is_valid():
                                    serializer.save()
                    if data['request_parameter_type']=='form-data':
                        if len(data.get('request_list')):
                            for i in data['request_list']:
                                if i.get('name'):
                                    i['api']=api_id
                                    serializer=APIParameterSerializer(data=i)
                                    if serializer.is_valid():
                                        serializer.save()
                    else:
                        raw_data =data.get('request_list')
                        if len(raw_data):
                            serializer=APIParameterRawSerializer(data={'api':api_id,'data':raw_data})
                            if serializer.is_valid():
                                serializer.save()
                    if len(data.get('response_list')):
                        for i in data['response_list']:
                            if i.get('name'):
                                i['api']=api_id
                                serializer=APIResponseSerializer(data=i)
                                if serializer.is_valid():
                                    serializer.save()
                    record_dynamic(project=project.id,_type='新增',operation_object='接口',user=request.user.pk,data='新增接口"%s"' % data['name'])
                    return JsonResponse(code=code.CODE_SUCCESS,data={'api_id':api_id})
                return JsonResponse(code=code.CODE_Failed)

