from . import views
from django.urls import path

app_name = "record"

urlpatterns = [
    path('', views.record_list, name='record_list'),
]

