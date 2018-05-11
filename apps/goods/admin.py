from django.contrib import admin

# Register your models here.
from apps.goods.models import GoodsSKU, GoodsCategory, IndexSlideGoods, GoodsSPU, IndexPromotion

admin.site.register(GoodsCategory)
admin.site.register(GoodsSPU)
admin.site.register(GoodsSKU)
admin.site.register(IndexSlideGoods)
admin.site.register(IndexPromotion)