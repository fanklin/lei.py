from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU
from utils.common import LoginRequiredMixin


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
        val = strict_redis.hget(key, sku_id)
        if val:
            count += int(val)

        # 库存判断
        if count > sku.stock:
            return JsonResponse({'code:5', 'errmsg：库存不足'})

        # 操作redis数据库存储商品到购物车
        strict_redis.hset(key, sku_id, count)

        # 查询购物车中商品的总数量
        total_count = 0
        vals = strict_redis.hvals(key)
        for val in vals:
            total_count +=int(val)

        # json方式响应添加购物车结果
        context ={
            'code': 0,
            'total_count': total_count,
        }

        return JsonResponse(context)


class CartInfoView(LoginRequiredMixin, View):
    """显示购物车界面"""

    def get(self, request):
        user_id = request.user.id
        # 从redis数据库查询出购物车的商品id
        strict_redis = get_redis_connection()
        key='cart_%s' % user_id
        sku_ids = strict_redis.hkeys(key)

        # 购物车界面显示的商品
        skus = []

        # 购物车商品总数量
        total_count = 0
        # 购物车商品总金额
        total_amount = 0

        for sku_id in sku_ids:
            # 从mysql数据库查询出商品对象
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
                # 商品的数量
                count = strict_redis.hget(key, sku_id)
                count = int(count)
                # 商品的小计金额
                amount = sku.price * count
                skus.append(sku)

                total_count += count
                total_amount += amount
                # 动态的给sku添加对象属性
                sku.count = count
                sku.amount = amount
            except:
                pass

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount
        }

        return render(request, 'cart.html', context)


class CartUpdateView(View):

    def post(self,request):

        """修改购物车商品数量"""
        # 判断登陆状态
        if not request.user.is_authenticated:
            return JsonResponse({'code':1, 'errmsg':'请先登陆'})

        # 获取请求参数
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')



        # 参数合法性判断
        if not all([sku_id,count]):
            return JsonResponse({'code':2, 'errmsg':'参数不能为空'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code':3, 'errmsg':'商品不存在'})

        try:
            count = int(count)
        except:
            return JsonResponse({'code':4, 'errmsg':'购买数量需为整数'})
        if count > sku.stock:
            return JsonResponse({'code':5, 'errmsg':'库存不足'})

        # todo:业务处理：保持 购物车商品数量
        strict_redis = get_redis_connection()

        key = 'cart_%s'%request.user.id
        strict_redis.hset(key,sku_id,count)

        # 响应json
        return JsonResponse({'code':0, 'errmsg':'修改成功'})


class CartDeleteView(View):
    def post(self,request):
        """删除购物车的商品"""
        # 判断是否有登陆
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登陆'})
        # 获取请求参数
        sku_id = request.POST.get('sku_id')



        # 业务处理：删除商品

