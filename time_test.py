import time

# 当前时间
now_time = time.time()
print('当前时间戳:'+str(now_time))

# 转换成日期格式
otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time))
print('日期格式:'+str(otherStyleTime))
