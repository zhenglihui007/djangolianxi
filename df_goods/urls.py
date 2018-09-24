from django.conf.urls import url
from . import views
# 接收根目录URL的路径并匹配到相应的视图函数
urlpatterns = [
    url(r'^$', views.index),
    url(r'^list(\d+)_(\d+)_(\d+)/$',views.goodlist),
    url(r'^(\d+)/$', views.detail),
]