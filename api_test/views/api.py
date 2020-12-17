from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import get_availability_project, record_dynamic, objects_paginator
from api_test.common.parameter_check import project_status_check, parameter_ids_check
from api_test.models import Project, APIInfo, APIGroup, APIHead, APIParameterRaw, APIParameter, APIResponse
from api_test.serializer import APIParameterSerializer, APIParameterRawSerializer, \
    APIResponseSerializer, APIInfoDeserializer, APIHeadSerializer, APIInfoListSerializer, APIInfoSerializer


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


class APIList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        result = project_status_check(request)
        if result:
            return result
        project_id,api_group_id,name=request.GET.get('project_id'),request.GET.get('api_group_id'),request.GET.get('name')
        if api_group_id:
            if not api_group_id.isdecimal():
                return JsonResponse(code=code.CODE_PARAMETER_ERROR)
            if name:
                objects=APIInfo.objects.filter(project=project_id,name__contains=name,api_group=api_group_id).order_by('id')
            else:
                objects = APIInfo.objects.filter(project=project_id, api_group=api_group_id).order_by('id')
        else:
            if name:
                objects=APIInfo.objects.filter(project=project_id,name__contains=name).order_by('id')
            else:
                objects = APIInfo.objects.filter(project=project_id).order_by('id')

        result = objects_paginator(request, objects)
        serialize = APIInfoListSerializer(result['obm'], many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": result['page'],
                                  "total": result['total']
                                  }, code=code.CODE_SUCCESS)


class APIInfoView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取接口详情
        :param request:
        :return:
        """
        api_id=request.GET.get('api_id')
        if not api_id or not api_id.isdecimal():
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        result=project_status_check(request)
        if result:
            return result
        try:
            api_info=APIInfo.objects.get(id=api_id,project=request.GET.get('project_id'))
            serializer=APIInfoSerializer(api_info)
            return JsonResponse(data=serializer.data,code=code.CODE_SUCCESS)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='接口不存在')


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


class UpdateAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        修改接口
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=all_parameter_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            api=APIInfo.objects.get(id=data['id'])
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='接口不存在')
        with transaction.atomic():
            serializer=APIInfoDeserializer(data=data)
            if serializer.is_valid():
                data['update_user']=request.user
                try:
                    if not isinstance(data.get('api_group_id'),int):
                        return JsonResponse(code=code.CODE_PARAMETER_ERROR)
                    APIGroup.objects.get(id=data['api_group_id'],project=data['project_id'])
                    User.objects.get(id=request.user.pk)
                    serializer.update(instance=api,validated_data=data)
                except KeyError:
                    User.objects.get(id=request.user.pk)
                    serializer.update(instance=api,validated_data=data)
                except ObjectDoesNotExist:
                    return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='分组不存在')
                header=Q()
                if len(data.get('headDict')):
                    for i in data['headDict']:
                        if i.get('api') and i.get('id'):
                            header=header|Q(id=i['id'])
                            if i['name']:
                                header_serializer=APIHeadSerializer(data=i)
                                if header_serializer.is_valid():
                                    i['api']=APIInfo.objects.get(id=i['api'])
                                    header_serializer.update(instance=APIHead.objects.get(id=i['id']),validated_data=i)
                        else:
                            if i.get("name"):
                                i['api']=data['id']
                                header_serializer=APIHeadSerializer(data=i)
                                if header_serializer.is_valid():
                                    header_serializer.save(api=APIInfo.objects.get(id=data['id']))
                                    header=header|Q(id=header_serializer.data.get('id'))
                test=APIHead.objects.filter(api=data['id'])
                APIHead.objects.exclude(header).filter(api=data['id']).delete()

                api_param=Q()
                api_param_raw=Q()
                if len(data.get('requestList')):
                    if data['request_parameter_type']=="form-data":
                        APIParameterRaw.objects.filter(api=data['id']).delete()
                        for i in data["requestList"]:
                            if i.get('api') and i.get('id'):
                                api_param=api_param |Q(id=i['id'])
                                if i['name']:
                                    param_serializer=APIParameterSerializer(data=i)
                                    if param_serializer.is_valid():
                                        i['api']=APIInfo.objects.get(id=i['api'])
                                        param_serializer.update(instance=APIParameter.objects.get(id=i['id']),
                                                                validated_data=i)
                            else:
                                if i.get('name'):
                                    i['api']=data['id']
                                    param_serializer=APIParameterSerializer(data=i)
                                    if param_serializer.is_valid():
                                        param_serializer.save(api=APIInfo.objects.get(id=data['id']))
                                        api_param=api_param|Q(id=param_serializer.data.get('id'))
                    else:
                        try:
                            object=APIParameterRaw.objects.get(api=data['id'])
                            object.data=data['requestList']
                            object.save()
                        except ObjectDoesNotExist:
                            object=APIParameterRaw(api=APIInfo.objects.get(id=data['id']),data=data['requestList'])
                            object.save()
                        api_param_raw=api_param_raw|Q(id=object.id)
                APIParameter.objects.exclude(api_param).filter(api=data['id']).delete()
                APIParameterRaw.objects.exclude(api_param_raw).filter(api=data['id']).delete()
                api_response=Q()
                if len(data.get('requestList')):
                    for i in data['requestList']:
                        if i.get('api') and i.get('id'):
                            api_response=api_response|Q(id=i['id'])
                            if i['name']:
                                response_serializer=APIResponseSerializer(data=i)
                                if response_serializer.is_valid():
                                    i['api']=APIInfo.objects.get(id=i['api'])
                                    response_serializer.update(instance=APIResponse.objects.get(id=i['id']),
                                                               validated_data=i)
                        else:
                            if i.get('name'):
                                i['api']=data['id']
                                response_serializer=APIResponseSerializer(data=i)
                                if response_serializer.is_valid():
                                    response_serializer.save(api=APIInfo.objects.get(id=data['id']))
                                    api_response=api_response|Q(id=response_serializer.data.get('id'))
                APIResponse.objects.exclude(api_response).filter(api=data['id']).delete()
                record_dynamic(project=data['project_id'],_type='修改',operation_object='接口',user=request.user.pk,
                               data='修改接口"%s"' % data['name'])
                return JsonResponse(code=code.CODE_SUCCESS)
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)


class DelAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        删除接口
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_ids_check(data) if isinstance(project,Project) else project
        if result:
            return result
        id_list=Q()
        for i in data['ids']:
            id_list=id_list|Q(id=i)
        api_list=APIInfo.objects.filter(id_list,project=data['project_id'])
        name_list=[]
        for j in api_list:
            name_list.append(str(j.name))
        with transaction.atomic():
            api_list.delete()
            record_dynamic(project=project.id,_type='删除',operation_object='接口',user=request.user.pk,data="删除接口分组，列表“%s”" % name_list)
            return JsonResponse(code=code.CODE_SUCCESS)
