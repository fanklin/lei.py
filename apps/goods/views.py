from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from redis.client import StrictRedis
from whoosh.externalsort import sort

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods, GoodsSKU
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
    """商品详情显示界面"""
    def get(self, request, sku_id):
        # 查询数据库中的数据
        # 所有的类别
        categories = GoodsCategory.objects.all()
        # 当前要显示的商品sku
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # return HttpResponse('商品不存在')
            return redirect(reverse('goods:index'))
        # 新品推荐
        new_skus = GoodsSKU.objects.filter(category=sku.category) \
                       .order_by('-create_time')[0:2]  # 取出两个数据(包含头不包含尾)

        # todo:其他规格商品sku
        # 购物车数量
        # 购物车商品数据
        cart_count = 0

        if request.user.is_authenticated():  # 已经登录
            strict_redis = get_redis_connection('default')
            key = 'cart_%s' % request.user.id

            # 获取所有的数量（列表）
            values = strict_redis.hvals(key)

            for count in values:
                cart_count += int(count)  # count为字符串

        # 保存用户浏览的商品记录到redis
        context = {
            'sku':sku,
            'categories':categories,
            'cart_count':cart_count,
            'new_skus':new_skus,
        }

        return render(request, 'detail.html',context)


class ListView(View):
    """商品列表界面"""
    def get(self, request, category_id, page_num):
        # 获取请求参数  获取排序条件
        sort = request.GET.get('sort')
        # 所有的类别
        categories = GoodsCategory.objects.all()
        # 当前类别对象
        try:
            category = GoodsCategory.objects.filter(id=category_id)
        except GoodsCategory.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 当前类别所有的商品
        if sort == 'price':
            skus = GoodsSKU.objects.filter(category=category).order_by('price')
        elif sort == 'hot':  # 销量从高到底
            skus = GoodsSKU.objects.filter(category=category).order_by('-sales')
        else:
            skus = GoodsSKU.objects.filter(category=category)
            sort = 'default'
        # 新品推荐
        new_skus = GoodsSKU.objects.filter(category=category) \
                       .order_by('-create_time')[0:2] # 获取两条数据
        # 购物车数量
        cart_count = 0

        if request.user.is_authenticated():  # 已经登录
            strict_redis = get_redis_connection('default')
            key = 'cart_%s' % request.user.id

            # 获取所有的数量（列表）
            values = strict_redis.hvals(key)

            for count in values:
                cart_count += int(count)  # count为字符串
        # 分页数据

        context = {
            'category': category,
            'categories': categories,
            'skus': skus,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,

        }



        return render(request, 'list.html', context)