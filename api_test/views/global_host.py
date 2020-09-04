from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import record_dynamic, get_availability_project
from api_test.common.parameter_check import parameter_ids_check
from api_test.models import Project, GlobalHost
from api_test.serializer import HostSerializer


def all_parameter_check(data):
    """
    验证所有表单数据
    :param data: 表单数据
    :return:返回检查结果
    """
    try:
        if not isinstance(data['project_id'],int) or not data["name"] or not data["host"]:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


def parameter_id_check(data):
    """
    验证host/project id
    :param data:
    :return:
    """
    try:
        if not isinstance(data['host_id'],int) or not isinstance(data['project_id'],int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


class AddHost(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        添加host
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=all_parameter_check(data) if isinstance(project,Project) else project
        if result:
            return result
        host=GlobalHost.objects.filter(name=data['name'],project=data['project_id'])
        if host:
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME,msg='存在同名host')
        serializer=HostSerializer(data=data)
        with transaction.atomic():
            if serializer.is_valid():
                serializer.save(project=project)
                record_dynamic(project=data['project_id'], _type='添加host', operation_object='域名', user=request.user.pk,
                               data=data['name'])
                return JsonResponse(data={"host_id":serializer.data.get("id")},
                                    code=code.CODE_SUCCESS)
            return JsonResponse(code=code.CODE_Failed)


class HostTotal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取host列表
        :param request:
        :return:
        """
        try:
            page_size=int(request.GET.get("page_size",20))
            page=int(request.GET.get("page",1))
        except (TypeError,ValueError):
            return JsonResponse(code=code.CODE_KEY_ERROR,msg="page and page size must be integer")
        project_id=request.GET.get('project_id')
        if not project_id.isdecimal():
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        try:
            project=Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST)
        if not project.status:
            return JsonResponse(code=code.CODE_PROJECT_DISABLE,msg="项目已经被禁用")
        name=request.GET.get('name')
        if name:
            hosts=GlobalHost.objects.filter(name__contains=name,project=project_id).order_by('id')
        else:
            hosts=GlobalHost.objects.filter(project=project_id).order_by('id')
        paginator=Paginator(hosts,page_size)
        total=paginator.num_pages
        try:
            obm=paginator.page(page)
        except PageNotAnInteger:
            obm=paginator.page(1)
        except EmptyPage:
            obm=paginator.page(paginator.num_pages)
        serializer=HostSerializer(obm,many=True)
        return JsonResponse(data={"data":serializer.data,
                                  "page":page,
                                  "total":total
                                  },code=code.CODE_SUCCESS)


class DelHost(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self, request):
        """
        删除域名
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_ids_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            for i in data['ids']:
                host=GlobalHost.objects.get(id=i)
                if host:
                    name=host.name
                    host.delete()
                    record_dynamic(project=data['project_id'],_type='删除', operation_object='域名',user=request.user.pk,data=host.name)
            return JsonResponse(code=code.CODE_SUCCESS)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='项目不存在！')


class UpdateHost(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        更新项目host
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_id_check(data) or all_parameter_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            host=GlobalHost.objects.get(id=data['host_id'])
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='未找到指定host')
        same_name_hosts=GlobalHost.objects.filter(name=data['name'], project=data['project_id'])
        if len(same_name_hosts):
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME,msg='host名称已占用')
        serialzier=HostSerializer(data=data)
        with transaction.atomic():
            if serialzier.is_valid():
                serialzier.update(instance=host,validated_data=data)
                record_dynamic(project=data['project_id'],_type='修改', operation_object='域名',user=request.user.pk,data=host.name)
                return JsonResponse(code=code.CODE_SUCCESS)
            return JsonResponse(code=code.CODE_Failed)


class EnableHost(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        启用host
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_id_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            host=GlobalHost.objects.get(id=data['host_id'],project=data['project_id'])
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='未找到指定host')
        host.status=not host.status
        host.save()
        _type = '启用' if host.status else '禁用'
        record_dynamic(project=data['project_id'], _type=_type, operation_object='域名', user=request.user.pk,
                       data=host.name)
        return JsonResponse(code=code.CODE_SUCCESS)


