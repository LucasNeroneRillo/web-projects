from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listings/<str:primary_key>", views.listings, name="listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("close", views.close, name="close"),
    path("comment", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:title>", views.category, name="category")
]
