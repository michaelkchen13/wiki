from django.urls import path

from . import views

urlpatterns = [
    path("wiki", views.index, name="index"),
    path("wiki/<str:title>", views.article, name="article"),
    path("wiki/new_article", views.newArticle, name="newArticle"),
    path("wiki/<str:editTitle>/edit", views.edit, name="edit"),
    path("wiki/search/<str:searchQuery>", views.search, name="search")
]
