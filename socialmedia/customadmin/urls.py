from django.urls import path
from . import views

app_name = 'customadmin'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('posts/', views.post_list, name='post_list'),
    path('reels/', views.reel_list, name='reel_list'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('posts/delete/<str:post_id>/', views.delete_post, name='delete_post'),
    path('reels/delete/<str:reel_id>/', views.delete_reel, name='delete_reel'),
    path('users/toggle-block/<int:user_id>/', views.toggle_block_user, name='toggle_block_user'),
]