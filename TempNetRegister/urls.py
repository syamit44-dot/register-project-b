"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from app import views
from django.urls import re_path as url

urlpatterns = [
    path('admin/', admin.site.urls),
    # url(r'^api/profile-user$', views.Profile_User),
    # url(r'^api/profile-auditor$', views.Profile_Auditor),
    # url(r'^api/profile-auditor/farms$', views.Profile_Auditor_Farms),

    # url(r'^api/v2/((?:user)|(?:auditor))?/login(?:/(?P<cmd>\w+))?/?$', views.UserLogin),
    # url(r'^api/v2/((?:user)|(?:auditor))?/refresh(?:/(?P<cmd>\w+))?/?$', views.UserRefresh),
    # url(r'^api/v2/((?:user)|(?:auditor))?/logout(?:/(?P<cmd>\w+))?/?$', views.UserLogout),
    # url(r'^api/v2/((?:user)|(?:auditor))?/password(?:/(?P<cmd>\w+))?/?$', views.UserPassword),

    # url(r'^api/register-farm$', views.RegisterFarm, {'cmd': None})
    url(r'^api/check-key$', views.CheckKey , {'cmd': None}),
    url(r'^api/signin$', views.Api_SignIn , {'cmd': None}),
    url(r'^api/signin/admin$', views.Api_SignIn , {'cmd': 'admin'}),
    url(r'^api/signup$', views.Api_SignUp , {'cmd': None}),

    # url(r'^api/getotp$', views.Api_GetOTP , {'cmd': None}),
    # url(r'^api/reset-password$', views.Api_ResetPassword , {'cmd': None}),

    url(r'^api/generate$', views.Api_AccessKey , {'cmd': None}),
    url(r'^api/refresh$', views.Api_RefreshToken , {'cmd': None}),
    url(r'^api/logout$', views.Api_Logout , {'cmd': None}),
    url(r'^api/equipment-models$', views.Api_EquipmentModels),
    url(r'^api/get-farm/user$', views.Api_GetFarm , {'cmd': 'user'}),
    path('api/farms/<int:farm_id>/icon', views.Api_FarmIcon),
    url(r'^api/get-farm/admin$', views.Api_GetFarm , {'cmd': 'admin'}),
    url(r'^api/request/new$', views.Api_RequestFarm , {'cmd': 'create'}),
    url(r'^api/request/update$', views.Api_RequestFarm , {'cmd': 'update'}),
    url(r'^api/admin/farm/(?P<farm_id>\d+)/(?P<cmd>approve|reject)$', views.Api_AdminFarmStatus),
    url(r'^api/admin/farm/(?P<farm_id>\d+)$', views.Api_AdminFarmDelete),
    url(r'^api/admin/request/update$', views.Api_AdminRequestUpdate),
]
