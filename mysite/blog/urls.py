from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


app_name = 'blog'

urlpatterns = [
     path('', views.post_list, name='post_list'),
     path('register/', views.user_register, name='user_register'),
     path('create/', views.PostCreateView.as_view(), name='post_create'),
     path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
     path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
     path('<int:post_id>/share/',
          views.post_share, name='post_share'),
     path('<int:post_id>/comment/',
          views.post_comment, name='post_comment'),
     path('', include('django.contrib.auth.urls')),

]