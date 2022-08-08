from django.urls import path

from . import views

urlpatterns = [
    path('', views.path_index, name='path_index'),
    path('truck_info/<int:id>', views.truck_info_view, name='truck_info_view'),
]
