from django.urls import path
from . import views

urlpatterns = [
    path('create_user/', views.CreateUserAPI.as_view(), name='register'),
    path('login/', views.LoginAPI.as_view(), name='login-api'),
    path('delete_user/', views.DeleteUserAPI.as_view(), name='delete-user'),
    path('get_user_by_username/', views.GetUserByUsernameAPI.as_view(), name='get-user-by-username'),
    path('get_user_by_name/', views.GetUserByNameAPI.as_view(), name='get-user-by-name'),
    path('update_user/<str:username>/', views.UpdateUserAPI.as_view(),
         name='user-details-update'),
    path('list_users/', views.GetUsersListAPI.as_view(), name='users-list'),
]
