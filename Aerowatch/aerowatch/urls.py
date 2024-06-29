from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("login", views.user_login,name="login"),
    path("register",views.register,name="register"),
    path("logout",views.logout_view,name="logout"),
    path("search/<str:filter>/<str:icao>",views.search,name="search"),
    path("route/<str:d_icao>/<str:a_icao>",views.route,name="route")
]

