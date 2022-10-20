
from django.urls import path

from . import views

urlpatterns = [
    path("", views.redirect_view),
    path("<int:page>", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:user>/<int:page>", views.user_profile, name="user_profile"),
    path("following/<int:page>", views.following_view, name="following"),
    path("posts/<int:post_id>", views.edit_post, name="edit"),
    
]
