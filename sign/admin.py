from django.contrib import admin
from sign.models import Event, Guest

# Register your models here.
# 让页面上展示的发布会展示更多的字段，增加EventAdmin和GuestAdmin
class EventAdmin(admin. ModelAdmin):
    list_display = ['name', 'status', 'start_time', 'id']
    # 快速生成搜索栏和过滤器
    search_fields = ['name']        # 搜索栏
    list_filter = ['status']        # 过滤器

class GuestAdmin(admin. ModelAdmin):
    list_display = ['realname', 'phone', 'email', 'sign', 'create_time', 'event']
    search_fields = ['realname','phone']     # 搜索栏
    list_filter = ['sign']                  # 过滤器

admin.site.register(Event, EventAdmin)
admin.site.register(Guest, GuestAdmin)
