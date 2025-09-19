from django.contrib import admin
from django.urls import path
from socialmedia import settings
from userauth import views
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home),
    path('loginn/',views.loginn),
    path('signup/',views.signup),
    path('logoutt/',views.logoutt),
    path('upload',views.upload),
    path('upload-reel', views.upload_reel, name='upload-reel'),
    path('like-post/<str:id>', views.likes, name='like-post'),
    path('like-reel/<str:id>', views.like_reel, name='like-reel'),
    path('#<str:id>', views.home_post),
    path('explore',views.explore),
    path('reels', views.reels_view, name='reels'),
    path('profile/<str:id_user>', views.profile),
    path('delete/<str:id>', views.delete),
    path('delete-reel/<str:id>', views.delete_reel),
    path('search-results/', views.search_results, name='search_results'),
    path('follow', views.follow, name='follow'),
    path('add-comment/<str:id>', views.add_comment, name='add-comment'),
    path('delete-comment/<str:id>', views.delete_comment, name='delete-comment'),
]