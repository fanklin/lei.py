from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU
from apps.users.models import Address
from utils.common import LoginRequiredMixin


class OrderPlace(LoginRequiredMixin,View):
    def post(self,request):
        """确认订单页面"""
        # 获取请求参数：sku_ids
        sku_ids = request.POST.getlist('sku_id')
        # 校验参数不能为空
        if not sku_ids:
            return redirect(reverse('cart:info'))
        # 获取用户地址信息(此处使用最新添加的地址)
        user = request.user
        try:
            address = Address.objects.filter(user=user).latest('create_time')
        except Address.DoesNotExist:
            address = None

        skus = []
        total_count = 0
        total_amount = 0
        # todo: 查询购物车中的所有的商品
        strict_redis = get_redis_connection()
        cart_dict = strict_redis.hgetall('cart_%s' %request.user.id)
        # 循环操作每一个订单商品
        # 查询一个商品对象
        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id = sku_id)
            except:
                return redirect(reverse('cart:info'))
            # 获取商品数量和小计金额(需要进行数据类型转换)
            sku_count = cart_dict.get(sku_id.encode())
            sku_count = int(sku_count)
            sku_amount = sku_count * sku.price


            # 新增实例属性,以便在模板界面中显示
            sku.count = sku_count
            sku.sku_amount = sku_amount
            # 添加商品对象到列表中
            skus.append(sku)
            # 累计商品总数量和总金额
            total_count += sku_count
            total_amount += sku_amount
        # 运费(运费模块)
        trans_cost = 10

        # 实付金额
        total_pay = total_amount +trans_cost


        # 定义模板显示的字典数据
        context = {
            'skus': skus,
            'total_amount': total_amount,
            'total_count': total_count,
            'trans_cost': trans_cost,
            'total_pay': total_pay,
            'address': address

        }

        # 响应结果: 返回确认订单html界面
        return render(request, 'place_order.html',context)