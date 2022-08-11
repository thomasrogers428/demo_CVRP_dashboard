# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    # Auth routes - login / register
    path("", include("apps.authentication.urls")),

    # ADD NEW Routes HERE
    path('demands/', include('demands.urls')),
    path('paths/', include('paths.urls')),
    path('logs/', include('logs.urls')),
    path('trucks/', include('trucks.urls')),

    # Leave `Home.Urls` as last the last line
    path("", include("apps.home.urls"))
]
