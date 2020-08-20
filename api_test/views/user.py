from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.serializer import TokenSerializer


class ObtainAuthToken(APIView):
    serializer_class=AuthTokenSerializer

    def post(self,request,*args,**kwargs):
        serializer=self.serializer_class(data=request.data,
                                         context={"request":request})
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data["user"]
        data=TokenSerializer(Token.objects.get(user=user)).data
        data['userphoto']='/file/userphoto.jpg'
        return JsonResponse(code=code.CODE_SUCCESS, msg="登录成功!", data=data)

# obtain_auth_token=ObtainAuthToken.as_view()
