from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("content/<int:buttonid>/", views.content, name="content"),
    path("collab/", views.collab, name="collab"),
    path("hybrid/",views.hybrid1,name="hybrid1"),
    path("profile/<str:car_id1>/",views.profile_view, name="profile_view"),
    path('5star/', views.fiveStar, name='star'),
    path('evCars/', views.evCars, name='ev'),
    path('support/', views.support, name='support')
]