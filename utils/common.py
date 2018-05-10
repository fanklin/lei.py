from django.contrib.auth.decorators import login_required
from django.views.generic import View


# 单继承
class LoginRequiredView(View):
    """判断是否有登录,没有登录,会跳转到登录界面"""

    # 需要声明为类方法
    @classmethod
    def as_view(cls, **initkwargs):
        # 获取视图函数
        view_fun = super().as_view(**initkwargs)
        # 通过方法调用的方式,对视图函数进行装饰
        return login_required(view_fun)



# 多继承: Mixin: 扩展功能,新增
class LoginRequiredMixin(object):
    """判断是否有登录,没有登录,会跳转到登录界面"""

    # 需要声明为类方法
    @classmethod
    def as_view(cls, **initkwargs):
        # 获取视图函数: 会调用View的as_view方法
        view_fun = super().as_view(**initkwargs)
        # 通过方法调用的方式,对视图函数进行装饰
        return login_required(view_fun)
