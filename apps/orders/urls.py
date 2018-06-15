from django.conf.urls import url

from apps.orders import views

urlpatterns = [
    url(r'^place$',views.OrderPlace.as_view(),name='place')

]