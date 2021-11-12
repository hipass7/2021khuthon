from . import views
from django.urls import path

urlpatterns = [
    path('', views.record_list, name='post_list'),
]
