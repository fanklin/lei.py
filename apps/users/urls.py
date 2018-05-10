from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from apps.users import views

urlpatterns = [

    # 视图函数
    # url(r'^register$', views.register, name='register'),
    # url(r'^do_register$', views.do_register, name='do_register'),

    # 类函数 (注意: as_view需要添加括号)
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^active/(?P<token>.+)$', views.ActiveView.as_view(), name='active'),

    url(r'^order$', views.UserOrderView.as_view(), name='order'),           # /users/order
    url(r'^address$', views.UserAddressView.as_view(), name='address'),     # /users/address
    url(r'^$', views.UserInfoView.as_view(), name='info'),                  # /users

    # View -> LoginRequiredView(重写as_view) -> UserAddressView
    # TemplateView -> LoginRequiredView2(重写as_view) -> UserAddressView

    # url(r'^address$', login_required(views.UserAddressView.as_view()), name='address'),     # /users/address
    # url(r'^address$', login_required(views.address), name='address'),     # /users/address

]