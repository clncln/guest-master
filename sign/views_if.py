from django.http import JsonResponse
from sign.models import Event,Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
import time


# 添加发布会接口
def add_event(request):
    eid = request.POST.get('eid','')                    # 发布会id
    name = request.POST.get('name','')                  # 发布会标题
    limit = request.POST.get('limit','')                # 限制人数
    status = request.POST.get('status','')              # 状态
    address = request.POST.get('address','')            # 地址
    start_time = request.POST.get('start_time','')      # 发布会时间

    # 首先，判断eid、name、limit、address、start_time等字段均不能为空，否则JsonResponse返回相应的状态码和提示信息
    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status':10021, 'message':'parameter error'})

    # 接着判断发布会id是否存在，若已存在，则返回对应的状态码和提示信息
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status':10022, 'message':'event id already exists'})

    # 接着判断发布会名称是否已存在，若已存在，则返回对应的状态码和提示信息
    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status':10023,'message':'event name already exists'})

    # 接着判断发布会状态是否为空，如果为空，则将状态设置为1（True）
    if status == '':
        status = 1

    # 最后，将数据插入到Event表，在插入过程中，如果日期格式错误，将抛出ValidationError异常接收该异常并返回响应的状态码和提示；
    try:
        Event.objects.create(id=eid,name=name,limit=limit,address=address,status=int(status),start_time=start_time)
    except ValidationError as e:
        error = 'start_time format error.It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status':10024,'message':error})

    # 若插入数据的均满足以上条件，则插入成功，返回状态码200和“add event success”的提示
    return JsonResponse({'status':200,'message':'add event success!'})


# 发布会查询接口
def get_event_list(request):
    # 通过GET请求接收发布会id和name参数，两个参数都是可选的
    eid = request.GET.get("eid","")        # 发布会id
    name = request.GET.get("name","")      # 发布会名称

    # 首先，判断两个参数是否同时为空，同时为空则返回错误码10021和参数错误的信息
    if eid == '' and name == '':
        return JsonResponse({'status':10021,'message':'parameter error'})

    # 如果发布会id不为空，优先通过id查询，因为id的唯一性，查询结果只会有一条
    if eid != '':
        event = {}
        # 如果id不存在，查询结果为空，则返回相应的状态码和提示信息
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022, 'message':'query result is empty'})
        # id存在，则将查询结果以key:value对的方式存放到定义的event字典中，并将数据字典作为整个返回字典中的data对应的值返回
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status':200, 'message':'success', 'data':event})

    # name查询为模糊查询，查询结果可能会有多条，首先将查询的每一条数据放到一个字典event中，再把每个字典放到数组datas中
    # 最后再将整个数组作为返回字典中的data对应的值返回
    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status':200,'message':'success','data':datas})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})


# 添加嘉宾接口
def add_guest(request):
    # 通过POST接口请求接收嘉宾参数，关联发布会id、姓名、手机号和邮箱等参数；
    eid = request.POST.get('eid', '')                    # 关联发布会id
    realname = request.POST.get('realname', '')          # 姓名
    phone = request.POST.get('phone', '')                # 手机号
    email = request.POST.get('email', '')                # 邮箱

    # 首先，判断eid、realname、phone等参数均不能为空
    if eid == '' or realname == '' or phone == '':
        return JsonResponse({'status':10021, 'message':'parameter error'})

    # 接着判断发布会id是否存在，如果不存在，则返回相应的状态码和提示信息
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status':10022, 'message':'event id null'})

    # 接着判断关联的发布会状态是否为True，如果不为True，则返回响应的状态码和提示信息
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status':10023, 'message':'event status is not available'})

    # 接着判断已添加的嘉宾数量和发布会限制人数，嘉宾数量大于等于发布会限制人数，说明发布会人数已满，不能再添加嘉宾，则返回相应的状态码和提示信息
    event_limit = Event.objects.get(id=eid).limit           # 发布会限制人数
    guest_limit = Guest.objects.filter(event_id=eid)        # 发布会已添加的嘉宾数

    if len(guest_limit) >= event_limit:
        return JsonResponse({'status':10024, 'meaasge':'event number is full'})

    # 判断当前时间是否大于发布会时间，如果大于则说明该发布会已经开始或者早已结束，那么该发布会就应该不能允许再添加嘉宾
    event_time = Event.objects.get(id=eid).start_time       # 发布会时间
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime, "%Y-%M-%D %H:%M:%S")
    e_time = int(time.mktime(timeArray))

    now_time = str(time.time())                             # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)

    if n_time >= e_time:
        return JsonResponse({'status':10025, 'message':'event has started'})

    # 最后，插入嘉宾数据，如果发布会的手机号重复，则抛出IntegrityError异常，接收该异常并返回相应的状态码和提示信息
    try:
        Guest.objects.create(realname=realname,phone=phone,email=email,sign=0,event_id=int(eid))

    except IntegrityError:
        return JsonResponse({'status':10026, 'message':'the event guest phone number repeat'})

    # 如果添加成功，则返回状态码200和“add guest success”的提示信息
    return JsonResponse({'status':200, 'message':'add guest success'})

# 嘉宾查询接口
def get_guest_list(request):
    # 通过GET请求接收发布会id和嘉宾手机号参数；
    eid = request.GET.get("eid","")                 # 关联发布会id
    phone = request.GET.get("phone","")             # 嘉宾手机号

    # 首先，判断发布会id是否为空，优先通过id查询；如果发布会id为空，则返回相应的状态码和提示信息
    if eid == '':
        return JsonResponse({'status':10021, 'message':'eid cannot be empty'})

    # 接着判断发布会id不为空并且嘉宾手机号为空的情况下，如果发布会id存在，则将查询的每一条数据放到一个字典guest中，
    # 再把每一个字典再放到数组datas中，最后将整个数组作为返回字典中的data对应的值返回
    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                datas.append(guest)
            return JsonResponse({'status':200, 'message':'success', 'data':datas})
        # 如果发布会id不存在，则返回相应的状态码和提示信息
        else:
            return JsonResponse({'status':10022, 'message':'query result is empty'})

    # 接着，判断发布会id和嘉宾手机号均不为空的情况
    if eid != '' and phone != '':
        guest = {}
        # 如果发布会id不存在，则返回相应的状态码和提示信息
        try:
            result = Guest.objects.get(phone=phone,event_id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022, 'message':'query result is empty'})
        # 如果发布会id存在，将查询结果以key:value对的方式存放在定义的guest字典中，并将数据字典作为整个返回字典中的data对应的值返回
        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status':200, 'message':'success', 'data':guest})

# 嘉宾签到接口
def user_sign(request):
    # 签到接口通过POST请求接收发布会id和嘉宾手机号；
    eid = request.POST.get('eid','')                    # 发布会id
    phone = request.POST.get('phone','')                # 嘉宾手机号

    # 首先，判断发布会id和嘉宾手机号两个参数均不能为空
    if eid == '' or phone == '':
        return JsonResponse({'status':10021, 'message':'parameter error'})

    # 接着判断发布会id是否存在，不存在则返回对应的状态码和提示信息
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status':10022, 'message':'event id null'})

    # 若发布会id存在，接着判断发布会状态是否为True，不为True，则返回状态码和提示信息
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status':10023, 'message':'event status is not available'})

    # 再接着判断当前时间是否大于发布会时间，首先获取发布会时间
    event_time = Event.objects.get(id=eid).start_time           # 发布会时间
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime,"%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))

    # 获取当前时间
    now_time = str(time.time())                                 # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)

    # 如果当前时间大于发布会时间，说明发布会已开始，不允许签到，返回对应的状态码和提示信息；如果当前时间小于发布会时间，说明发布会还未开始，可以签到，继续判断
    if n_time >= e_time:
        return JsonResponse({'status':10024, 'message':'event has started'})

    # 判断嘉宾的手机号是否存在，不存在则返回状态码和提示信息
    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status':10025, 'message':'user phone null'})

    # 判断嘉宾的手机号和发布会id是否为对应关系，若该手机号与发布会id没有关联，则返回状态码和提示信息
    result = Guest.objects.filter(event_id=eid,phone=phone)
    if not result:
        return JsonResponse({'status':10026, 'message':'user did not participate in the conference'})

    # 最后判断嘉宾的状态是否为已签到，如果已签到，返回对应的状态码和提示信息；
    result = Guest.objects.get(event_id=eid,phone=phone).sign
    if result:
        return JsonResponse({'status':10027, 'message':'user has sign in'})
    # 如果未签到，则修改状态为已签到，并返回状态码200和“sign success”的提示
    else:
        Guest.objects.filter(event_id=eid,phone=phone).update(sign='1')
        return JsonResponse({'status':200, 'message':'sign success'})




















