from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.code import CODE_SUCCESS
from api_test.common.common import record_dynamic, get_availability_project
from api_test.models import Project
from api_test.serializer import ProjectSerializer, ProjectDeserializer


def all_parameter_check(data):
    """
    验证所有表单数据
    :param data: 表单数据
    :return:返回检查结果
    """
    try:
        if not data["name"] or not data["version"] or not data["type"]:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR, msg="必选参数为空")
        if data["type"] not in ["Web", "App"]:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR, msg="项目类型参数错误")
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)

def project_id_check(data):
    """
    校验project_id正确性
    :param data:
    :return:
    """
    try:
        if not isinstance(data['project_id'], int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


class ProjectList(APIView):
    authentication_classes = [TokenAuthentication,]

    def get(self,request):
        """
        获取所有项目列表
        :param request:
        :return:
        """
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(not request.GET.get("page", 1))
        except(TypeError, ValueError):
            return JsonResponse(code='999985', msg="page and page_size must be integer")

        name = request.GET.get('name')
        if name:
            obi = Project.objects.filter(name__contains=name)
        else:
            obi = Project.objects.all().order_by('id')
        paginator = Paginator(obi, page_size)
        total = paginator.num_pages
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serializer = ProjectSerializer(obm, many=True)
        return JsonResponse(code=CODE_SUCCESS, data={"data": serializer.data,
                                                 "page": page,
                                                 "total": total})


class AddProject(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = ()

    def post(self,request):
        data=JSONParser().parse(request)
        result=all_parameter_check(data)
        if result:
            return result
        data["owner"]=request.user.pk
        project_serializer=ProjectDeserializer(data=data)
        try:
            Project.objects.get(name=data["name"])
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME)
        except ObjectDoesNotExist:
            with transaction.atomic():
                if project_serializer.is_valid():
                    project_serializer.save()
                    # 记录动态
                    record_dynamic(project=project_serializer.data.get('id'),_type='添加', operation_object='项目',
                                   user=request.user.pk,data=data['name'])
                    return JsonResponse(data={"project_id":project_serializer.data.get('id')},code=code.CODE_SUCCESS)
                else:
                    return JsonResponse(code.CODE_Failed)


class UpdateProject(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        修改项目
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        project = get_availability_project(data, request.user)
        result=all_parameter_check(data) or project_id_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            Project.objects.get(name=data["name"])
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME)
        except ObjectDoesNotExist:
            # 更新项目
            project_serializer=ProjectDeserializer(data=data)
            with transaction.atomic():
                if project_serializer.is_valid():
                    project_serializer.update(instance=project,validated_data=data)
                    record_dynamic(project=data['project_id'], _type='修改', operation_object='项目',
                                   user=request.user.pk, data=data['name'])
                    return JsonResponse(code=code.CODE_SUCCESS)
                else:
                    return JsonResponse(code=code.CODE_Failed)


class DelProject(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self,data):
        """
        校验删除id列表的有效性
        :param data:
        :return:
        """
        try:
            if not isinstance(data['ids'],list):
                return JsonResponse(code=code.CODE_PARAMETER_ERROR)
            for i in data['ids']:
                if not isinstance(i,int):
                    return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        except KeyError:
            return JsonResponse(code=code.CODE_KEY_ERROR)

    def post(self,request):
        """
        删除项目
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        result=self.parameter_check(data)
        if result:
            return result
        for i in data['ids']:
            try:
                project = Project.objects.get(id=i)
                if not request.user.is_superuser and project.owner.is_superuser:
                    return JsonResponse(code=code.CODE_PARAMETER_ERROR)
            except ObjectDoesNotExist:
                return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST, msg='项目不存在')
            try:
                project.delete()
            except Exception:
                return JsonResponse(code=code.CODE_Failed)
        return JsonResponse(code=code.CODE_SUCCESS)


class EnableProject(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        更改当前
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=project_id_check(data) if isinstance(project,Project) else project
        if result:
            return result
        # 项目状态取反
        project.status = not project.status
        project.save()
        # 判断启用/禁用
        _type = '启用' if project.status else '禁用'
        record_dynamic(project=data['project_id'], _type=_type, operation_object='项目',
                           user=request.user.pk, data=project.name)
        return JsonResponse(code=code.CODE_SUCCESS)


class ProjectInfo(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取单个项目信息
        :param request:
        :return:
        """
        project_id=request.GET.get('project_id')
        if not project_id and not project_id.isdecimal():
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        try:
            project_info=Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='项目不存在')
        serializer=ProjectSerializer(project_info)
        if serializer.data['status']:
            return JsonResponse(data=serializer.data,code=code.CODE_SUCCESS)
        else:
            return JsonResponse(code=code.CODE_PROJECT_DISABLE)
