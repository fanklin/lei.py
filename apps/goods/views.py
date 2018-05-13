from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from redis.client import StrictRedis
from django.core.cache import cache
from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods
from apps.users.models import User


class IndexView(View):


    def get(self,request):

        # 获取redis中的缓存数据
        context = cache.get('index_page_data')
        if context is None:
            print('没有缓存数据，从mysql中读取')
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
            #  查询当前类别所有的文字商品和图片商品
            for c in categories:
                text_skus = IndexCategoryGoods.objects.filter(
                    category=c,display_type=0).order_by('index')
                imgs_skus = IndexCategoryGoods.objects.filter(
                    category=c,display_type=1).order_by('index')
                # 动态地给类别对象,新增属性
                c.text_skus = text_skus
                c.imgs_skus = imgs_skus

            # 定义模板显示的数据
            context = {
                'categories': categories,
                'slide_goods': slide_goods,
                'promotions': promotions,

            }
            # 缓存数据
            # 参数1: 键
            # 参数2: 要缓存的数据
            cache.set('index_page_data', context, 3600)
        else:
            print('使用缓存')
        # 购物车商品数据
        cart_count = 0

        if request.user.is_authenticated():  # 已经登录
            strict_redis = get_redis_connection('default')
            key = 'cart_%s' % request.user.id

            # 获取所有的数量（列表）
            values = strict_redis.hvals(key)

            for count in values:
                cart_count += int(count)  # count为字符串

        # 新增购物车数量的键值
        context.update(cart_count=cart_count)


        return render(request, 'index.html', context)


class DetailView(View):
    """商品详情"""
    def get(self,request, sku_id):
        return render(request,'detail.html')
