from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/success/', views.signup_success_view, name='signup_success'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('problems/', views.problems_view, name='problems'),
    path('api/check-answer/', views.check_answer, name='check_answer'),
    
    # Admin URLs (using 'manage' prefix to avoid conflict with Django admin)
    path('admin-dashboard/', views.admin_view, name='admin'),
    path('manage/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage/promote/<int:user_id>/', views.promote_user, name='promote_admin'),
    path('manage/demote/<int:user_id>/', views.demote_user, name='demote_admin'),
    path('manage/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]