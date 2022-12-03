"""SuperNiubility URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from SuperNiubility import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path('login/action/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('change/', views.change, name="change"),
    path('register/', views.register, name="register"),
    path('code/', views.code, name="code"),
    path('email/', views.email, name="email"),

    path("nb/", include("nb.urls")),
    path("wx/", include("wx.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.page_not_found
handler500 = views.server_error
