from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('event/', views.event, name='event'),
    path('hot/title/', views.hot_title, name='hot_title'),
    path('hot/event/', views.hot_event, name='hot_event'),
]
