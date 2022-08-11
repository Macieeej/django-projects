from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("creator", views.creator, name="creator"),
    path("random", views.random, name="random"),
    path("editor/<str:TITLE>", views.editor, name="editor"),
    path("wiki/<str:TITLE>", views.wiki_page, name="wiki_page")
]
