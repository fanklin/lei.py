from django.conf.urls import url

from apps.cart import views

urlpatterns = [
    url(r'^add$', views.CartAddView.as_view(), name='add'),  # 添加商品到购物车
    url(r'^$', views.CartInfoView.as_view(), name='info'),  # 购物车页面显示
]