
from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import ModelAdmin
from django.core.cache import cache

from apps.goods.models import GoodsSKU, GoodsCategory, IndexSlideGoods, GoodsSPU, IndexPromotion, IndexCategoryGoods
from celery_tasks.tasks import generate_static_index_html


class BaseAdmin(admin.ModelAdmin):
    """模型管理类父类"""

    def save_model(self, request, obj, form, change):
        """管理员在管理后台新增/修改了数据后,会执行此方法"""
        super().save_model(request, obj, form, change)
        # 重新生成首页静态页面
        generate_static_index_html.delay()
        # 删除缓存数据
        cache.delete('index_page_data')


    def delete_model(self, request, obj):
        """管理员在管理后台删除数据后,会执行此方法"""
        super().delete_model(request, obj)
        # 重新生成首页静态页面
        generate_static_index_html.delay()
        # 删除缓存数据
        cache.delete('index_page_data')


class GoodsCategoryAdmin(BaseAdmin):
    pass


class GoodsSPUAdmin(BaseAdmin):
    pass


class GoodsSKUAdmin(BaseAdmin):
    pass


class IndexSlideGoodsAdmin(BaseAdmin):
    pass


class IndexPromotionAdmin(BaseAdmin):
    pass


class IndexCategoryGoodsAdmin(BaseAdmin):
    pass


admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(GoodsSPU,GoodsSKUAdmin)
admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(IndexSlideGoods,IndexSlideGoodsAdmin)
admin.site.register(IndexPromotion,IndexPromotionAdmin)
admin.site.register(IndexCategoryGoods, IndexCategoryGoodsAdmin)