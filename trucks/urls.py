from django.urls import path

from . import views

urlpatterns = [
    path('', views.trucks_index_view, name='trucks_index'),
    path('add/', views.trucks_add_view, name='trucks_add'),
    path('delete/', views.trucks_delete_view, name='trucks_delete'),
]
