# import os
# import django
# # 设置配置文件
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# # 初始化django环境
# django.setup()


from celery import Celery
from django.core.mail import send_mail

from dailyfresh import settings
# 创建celery客户端
app = Celery('dailyfresh', broker='redis://127.0.0.1:6379/1')


# 创建celery客户端
# 参数1: 自定义名称
# 参数2: 中间人 使用编号为1的数据库
@app.task
def send_active_mail(username, email, token):
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
                   '<a href="http://127.0.0.1:8000/usersactive/%s">' \
                   'http://127.0.0.1:8000/users/active/%s</a>' \
                   % (username, token, token)  # 邮件的正文
    send_mail(subject, message, form_email, recipient_list,
              html_message=html_message)  # 关键字参数