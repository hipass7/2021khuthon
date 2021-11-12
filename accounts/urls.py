from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('start/', views.start, name='start'),
    path('end/', views.end, name='end'),
    path('check/', views.check, name='check')
]
