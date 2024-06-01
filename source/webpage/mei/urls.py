# noinspection GrazieInspection
"""
URL configuration for mei project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from public.exception import CustomException
from django.urls import path

urlpatterns = []


def register_url(url):
    def get_fun(fun):
        for url_pattern in urlpatterns:
            if url_pattern.name == url:
                raise CustomException(f'异步服务器：重复注册：{url}')
        urlpatterns.append(path(url, fun, name=url))
        return fun

    return get_fun
