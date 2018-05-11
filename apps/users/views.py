import re


from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from pymysql.err import IntegrityError

from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
from celery_tasks.tasks import send_active_mail
from dailyfresh import settings
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired

from utils.common import LoginRequiredMixin


class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1.获取请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 2.校验输入合法性

        if not all([username, password, password2, email]):
            return render(request, 'register.html', {'errmsg': '参数不能为空'})

        if password != password2:
            return render(request, 'register.html', {'errmsg': '密码输入不一致'})

        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 同意用户协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意用户协议'})

        # 3.保存倒数据库,不能重复添加用户
        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError:  # 数据完整性错误  数据已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})


        # todo:给用户发送邮件
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 60*60)
        token = s.dumps({'confirm': user.id})     # btys
        token = token.decode()    # 转换成字符串

        # self.send_active_mail(username, email, token)

        # 使用celery异步发送邮件
        send_active_mail.delay(username, email, token)

        # 修改用户状态为未激活（默认为激活状态）
        user.is_active = False
        user.save()

        return HttpResponse('进入登录界面')


    def send_active_mail(self, username, email, token):
        """
        发送激活邮件
        :param username: 注册用户
        :param email: 注册用户的邮箱
        :param token: 对字典加密后的结果
        :return:
        """
        # 调用的django自带的send_mail方法

        subject = '天天生鲜注册激活'                # 邮件标题
        message = ''                # 邮件的正文（不带样式）
        form_email = settings.EMAIL_FROM             # 发送者
        recipient_list = [email]         # 接收者  需要生一个list
        html_message= '<h2>尊敬的 %s, 感谢注册天天生鲜</h2>' \
                    '<p>请点击此链接激活您的帐号: ' \
                    '<a href="http://127.0.0.1:8000/users/active/%s">' \
                    'http://127.0.0.1:8000/users/active/%s</a>' \
                    % (username, token, token)            # 邮件的正文
        send_mail(subject, message, form_email, recipient_list,
                  html_message=html_message) # 关键字参数


class ActiveView(View):

    def get(self, request, token):
        """激活注册帐号"""
        # token:对字典{‘confirm':用户id}加密后的结果
        try:
            # 对token进行解密
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600)

            # 解密后得到的是字典
            my_dict = s.loads(token)

            # 获取用户id
            user_id = my_dict.get('confirm')
        except SignatureExpired:
            return HttpResponse('url链接已过期')

        # 修改用户状态为已激活
        User.objects.filter(id=user_id).update(is_active=True)

        return HttpResponse('激活成功，进入登录界面')


class LoginView(View):
    def get(self, request):

        return render(request, 'login.html')

    def post(self,request):
        # 获取登录请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')  # 是否记录登录状态
        # 获取登录合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '用户名或密码不能为空'})
        # 判断用户名密码是否正确
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
        # 判断用户名是否激活
        if not user.is_active:
            return render(request, 'login.html', {'errmsg': '帐号未激活'})
        # 记录登录状态（session）
        # 内部会通过session保存用户的id
        login(request, user)

        # 设置session有效期
        if remember == 'on':  # 勾选保存用户状态
            request.session.set_expiry(None)   # 保存登录状态两周
        else:
            request.session.set_expiry(0)   # 关闭浏览器 清除session

        # 设置next跳转参数
        next_url = request.GET.get('next', None)
        if next_url is None:
            return redirect(reverse('goods:index'))
        else:
            return redirect(next_url)
        # 响应请求登录首页
        # return redirect(reverse('goods:index'))


class LogoutView(View):

    def get(self,request):
        """注销功能"""
        # 清除用户id
        logout(request)
        return redirect(reverse('goods:index'))



class UserInfoView(LoginRequiredMixin, View):

    def get(self,request):
        """进入个人信息"""
        user = request.user
        try:
            address = user.address_set.all().latest('create_time')
        except Address.DoesNotExist:
            address = None
        # 要从redis数据库中读取用户的浏览记录
        strict_redis = get_redis_connection()
        key = 'history_%s' % request.user.id
        # 最多只显示三个浏览记录
        sku_ids = strict_redis.lrange(key, 0, 2)
        skus = GoodsSKU.objects.filter(id__in=sku_ids)

        data = {'which_page': 0, 'address':address, 'skus': skus}
        return render(request, 'user_center_info.html', data)


class UserOrderView(LoginRequiredMixin, View):
    def get(self,request):
        """进入订单"""
        data = {'which_page': 1}
        return render(request, 'user_center_order.html', data)


class UserAddressView(LoginRequiredMixin, View):
    def get(self,request):
        """进入地址"""
        # 查询用户最新添加的地址
        user = request.user
        # address = Address.objects.filter(user=user)\
        # .order_by('-create_time')[0]
        # latest 表示获取最新添加的
        try:
            address = user.address_set.all().latest('create_time')
        except Address.DoesNotExist:
            address = None
        data = {'which_page': 2, 'address': address}
        return render(request, 'user_center_site.html', data)

    def post(self,request):
        """新增一个用户地址"""
        # 获取请求参数
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')

        # 判断参数合法性
        if not all([receiver,address,mobile]):
            return render(request, 'user_center_site.html', {'errmsg':'参数不能为空'})


        # 新增一个地址
        # address = Address()
        # address.receiver_name = receiver
        # address.receiver_mobile = mobile
        # address.save
        user = request.user
        Address.objects.create(
            receiver_name=receiver,
            receiver_mobile=mobile,
            detail_addr=address,
            zip_code=zip_code,
            user=user
        )

        # 响应请求
        return redirect(reverse('users:address'))