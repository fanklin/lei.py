from django.http.response import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU


class CartAddView(View):

    def post(self,request):
        """添加商品到购物车"""
        # 判断用户是否登陆
        if not request.user.is_authenticated():
            return JsonResponse({'code:1', 'errmsg：请先登陆'})
        # 接收数据：user_id，sku_id，count
        user_id = request.user.id
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 校验参数all()
        if not all([sku_id, count]):
            return JsonResponse({'code:2', 'errmsg：参数不能为空'})
        # 判断商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code:3', 'errmsg：商品不存在'})
        # 判断count是否是整数
        try:
            count = int(count)
        except Exception:
            return JsonResponse({'code:4', 'errmsg：购买数量需要为整数'})
        # 判断库存
        strict_redis = get_redis_connection()
        key = 'cart_%s' % user_id
        # 获取 不到会返回None
        val = strict_redis.hget(key,sku_id)
        if val:
            count += int(val)

        # 库存判断
        if count > sku.stock:
            return JsonResponse({'code:5', 'errmsg：库存不足'})

        # 操作redis数据库存储商品到购物车
        strict_redis.hset(key, sku_id, count)

        # 查询购物车中商品的总数量
        total_count = 0
        vals = strict_redis.hvals()
        for val in vals:
            total_count +=int(val)

        # json方式响应添加购物车结果
        context ={
            'code':0,
            'total_count':total_count,
        }

        return JsonResponse(context)
