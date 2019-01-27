from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout', auth_views.LogoutView.as_view(), {'next_page': 'index'}, name='logout'),
    path('create_sub', views.createSub, name='create_sub'),
]