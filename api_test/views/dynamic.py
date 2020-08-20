from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.models import Project, ProjectDynamic
from api_test.serializer import ProjectDynamicSerializer


class Dynamic(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取项目动态
        :param request:
        :return:
        """
        try:
            page_size=int(request.GET.get("page_size",20))
            page=int(request.GET.get("page",1))
        except(TypeError,ValueError):
            return JsonResponse(code=code.CODE_KEY_ERROR,msg="page and page size must be integer")
        project_id=request.GET.get('project_id')
        if not project_id.isdecimal():
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        try:
            project=Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg="项目不存在或已删除！")
        if not project.status:
            return JsonResponse(code=code.CODE_PROJECT_DISABLE)
        dynamics=ProjectDynamic.objects.filter(project=project_id).order_by('-time')
        paginator=Paginator(dynamics,page_size)
        total = paginator.num_pages
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serializer=ProjectDynamicSerializer(obm,many=True)
        return JsonResponse(data={"data":serializer.data,
                                  "page":page,
                                  "total":total},
                            code=code.CODE_SUCCESS)


