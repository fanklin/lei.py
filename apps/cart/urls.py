from django.conf.urls import url

from apps.cart import views

urlpatterns = [
    url(r'^add$', views.CartAddView.as_view(), name='add'),  # 添加商品到购物车
    # /cart/update  修改购物车商品数量
    url(r'^update$', views.CartUpdateView.as_view(), name='update'),
    url(r'^delete$', views.CartDeleteView.as_view(), name='delete'),

    url(r'^$', views.CartInfoView.as_view(), name='info'),  # 购物车页面显示
]