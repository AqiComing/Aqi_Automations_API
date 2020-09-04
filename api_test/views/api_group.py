from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import get_availability_project, record_dynamic, check_project_status
from api_test.common.parameter_check import parameter_id_check
from api_test.models import APIGroup, Project
from api_test.serializer import APIGroupSerializer


def check_name_parameter(data):
    try:
        if not data['name']:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR,msg='组名不能为空')
        same_name_group=APIGroup.objects.filter(name=data['name'],project=data['project_id'])
        if same_name_group:
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME,msg='存在同名分组')
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


class APIGroupView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取接口
        :param request:
        :return:
        """
        project = check_project_status(request)
        if not isinstance(project, Project):
            return project
        group_list=APIGroup.objects.filter(project=project.id).order_by('id')
        serializer=APIGroupSerializer(group_list,many=True)
        return JsonResponse(data=serializer.data,code=code.CODE_SUCCESS)


class APIGroupAdd(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        添加API分组
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=check_name_parameter(data) if isinstance(project,Project) else project
        if result:
            return result
        serializer=APIGroupSerializer(data=data)
        if serializer.is_valid():
            serializer.save(project=project)
            record_dynamic(project=project.id,_type="添加",operation_object='接口分组',user=request.user.pk,
                           data="新增接口分组'%s'" % data['name'])
            return JsonResponse(code=code.CODE_SUCCESS)
        return JsonResponse(code=code.CODE_Failed)


class DelAPIGroup(APIView):

    def post(self,request):
        """
        删除group
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_id_check(data) if (project,Project) else project
        if result:
            return result
        try:
            group = APIGroup.objects.get(id=data['id'],project=data['project_id'])
            group.delete()
            record_dynamic(project=project, _type='删除', operation_object='接口分组', user=request.user.pk,
                        data='删除接口分组"%s"' % group.name)
            return JsonResponse(code=code.CODE_SUCCESS)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='接口分组不存在')


class UpdateAPIGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        data=JSONParser().parse(request)
        user=request.user
        project=get_availability_project(data,request.user)
        result=parameter_id_check(data) or check_name_parameter(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            group = APIGroup.objects.get(id=data['id'],project=data['project_id'])
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='分组不存在')

        serializer=APIGroupSerializer(data=data)
        if serializer.is_valid():
            serializer.update(instance=group,validated_data=serializer.data)
            record_dynamic(project=project, _type='修改', operation_object='接口分组', user=request.user.pk,
                           data='修改接口分组"%s"' % group.name)
            return JsonResponse(code=code.CODE_SUCCESS)
        else:
            return JsonResponse(code=code.CODE_Failed)
