from django.urls import path

from . import views

urlpatterns = [
    path('', views.logs_index_view, name='logs_index'),
    path('logged_path_info/<int:id>', views.logged_path_info_view,
         name='logged_path_info_view'),
]
