from django.shortcuts import render
from django.views.generic import View

from apps.users.models import User


class IndexView(View):

    def get(self,request):
        # # 从session中获取登录用户id
        # user_id = request.session.get('_auth_user_id')
        # # 查询出登录的用户对象
        # user = User.objects.get(id=user_id)

        # 方式二
        # user = request.user
        # print('user=%s' %user.username)
        return render(request, 'index.html')