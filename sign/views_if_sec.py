from django.contrib import auth as django_auth
import hashlib
from django.utils.baseconv import base64
from django.http import JsonResponse

# 用户认证
def user_auth(request):
    get_http_auth = request.META.get('HTTP_AUTHORIZATION', b'')
    auth = get_http_auth.split()
    print(auth)
    try:
        auth_parts = base64.b64decode(auth[1]).decode('iso-8859-1').partition(':')

    except IndexError:
        return "null"

    userid, password = auth_parts[0], auth_parts[2]
    user = django_auth.authenticate(username=userid,password=password)
    if user is not None and user.is_active:
        django_auth.login(request, user)
        return "success"

    else:
        return "fail"

# 发布会查询接口 ---增加用户认证
def sec_get_event_list(request):
    auth_result = user_auth(request)        # 调用认证函数
    if auth_result == "null":
        return JsonResponse({'status':10011,'message':'user auth null'})

    if auth_result == 'fail':
        return JsonResponse({'status':10012,'message':'user auth fail'})

    eid = request.GET.get("eid", "")        # 发布会id
    name = request.GET.get("name", "")      # 发布会名称




















