# import os
# import django
# # 设置配置文件
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# # 初始化django环境
# django.setup()


from celery import Celery

from django.core.mail import send_mail
from django.template import loader

from apps.goods.models import IndexCategoryGoods, IndexPromotion, IndexSlideGoods, GoodsCategory
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

@app.task
def generate_static_index_html():

    # 查询所有商品类别
    categories = GoodsCategory.objects.all()

    # 轮播图商品
    slide_goods = IndexSlideGoods.objects.all().order_by('index')
    # 促销活动数据
    try:
        promotions = IndexPromotion.objects.all()[0:2]  # 只获取两个促销活动
    except:
        pass
    # 类别商品数据
    #  查询当前类别所有的文字商品和图片商品
    for c in categories:
        text_skus = IndexCategoryGoods.objects.filter(
            category=c, display_type=0).order_by('index')
        imgs_skus = IndexCategoryGoods.objects.filter(
            category=c, display_type=1).order_by('index')
        # 动态地给类别对象,新增属性
        c.text_skus = text_skus
        c.imgs_skus = imgs_skus

    # 购物车商品数据
    cart_count = 0

    # 定义模板显示的数据
    context = {
        'categories': categories,
        'slide_goods': slide_goods,
        'promotions': promotions,
        'cart_count': cart_count,
    }


    # 获取模板文件
    template = loader.get_template('index.html')
    # 渲染生成标准备的html内容
    html_str = template.render(context)

    # 生成一个叫index.html的文件: 放在桌面的static目录下
    file_path = '/home/python/Desktop/static/index.html'
    with open(file_path, 'w') as file:
        # 写入html内容
        file.write(html_str)

