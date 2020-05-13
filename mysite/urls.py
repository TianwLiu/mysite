"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from mysite import settings
from mysite.views import *
from tool.views import index_tool,index_uploadsonglist,index_listmanager,index_player

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', default),
    path('hello/<int:first>/<int:second>',hello),
    path('gettime/<str:name>/',get_currenttime),
    path('audioplayer/<str:song_name>/',audioplayer),
    path('download/<str:song_name>/',download),
    path('player/',index_player),
    path('listmanager/',index_listmanager),
    path('uploadsonglist/',index_uploadsonglist),
    path('tool/',index_tool),

]


