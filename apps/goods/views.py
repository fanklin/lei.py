from django.shortcuts import render
from django.views.generic import View

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods
from apps.users.models import User


class IndexView(View):

    # def get(self,request):
    #     # # 从session中获取登录用户id
    #     # user_id = request.session.get('_auth_user_id')
    #     # # 查询出登录的用户对象
    #     # user = User.objects.get(id=user_id)
    #
    #     # 方式二
    #     # user = request.user
    #     # print('user=%s' %user.username)
    #     return render(request, 'index.html')

    def get(self,request):
        # 查询首页要显示的数据

        # 查询所有商品类别
        categories = GoodsCategory.objects.all()

        # 轮播图商品
        slide_goods = IndexSlideGoods.objects.all().order_by('index')
        # 促销活动数据
        try:
            promotions = IndexPromotion.objects.all()[0:2] # 只获取两个促销活动
        except :
            pass
        # 类别商品数据
        for c in categories:
            text_skus = IndexCategoryGoods.objects.filter(
                category=c,display_type=0).order_by('index')
            imgs_skus = IndexCategoryGoods.objects.filter(
                category=c,display_type=1).order_by('index')

            c.text_skus = text_skus
            c.imgs_skus = imgs_skus
        # for c in categories:
        #     # 查询当前类别所有的文字商品和图片商品
        #     text_skus = IndexCategoryGoods.objects.filter(
        #         category=c, display_type=0).order_by('index')
        #     imgs_skus = IndexCategoryGoods.objects.filter(
        #         category=c, display_type=1).order_by('index')
        #     # 动态地给类别对象,新增属性
        #     c.text_skus = text_skus
        #     c.imgs_skus = imgs_skus

        # 购物车商品数据
        cart_count = 0
        # 定义模板显示的数据
        context = {
            'categories': categories,
            'slide_goods': slide_goods,
            'promotions': promotions,
            'cart_count': cart_count,
        }

        # 响应请求，显示模板

        return render(request, 'index.html', context)