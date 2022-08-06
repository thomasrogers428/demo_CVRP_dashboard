from django.urls import path

from . import views

urlpatterns = [
    path('', views.demand_index, name='demand_index'),
    path('add/', views.add, name='add'),
    path('delete/', views.delete, name='delete'),
]
