from django.urls import   path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('',views.home, name='home'),
    path('signin',views.signin, name='signin'),
    path('signup',views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('signout',views.signout, name='signout'),
    path('home',views.home, name='home'),
    path('back_admin',views.back_admin, name='back_admin'),
    path('back_user',views.back_user, name='back_user'),
    path('add_tests',views.add_tests, name='add_tests'),
    path('add_videos',views.add_videos, name='add_videos'),
    path('view_grade',views.view_grade, name='view_grade'),
    path('view_announcement',views.view_announcement, name='view_announcement'),
    path('add_Announcement',views.add_Announcement, name='add_Announcement'),
    path('view_adminTest',views.view_adminTest, name='view_adminTest'),
    path('test_delete',views.test_delete, name='test_delete'),
    path('delete_Announcement',views.delete_Announcement,name='delete_Announcement'),
    path('update_test',views.update_test, name='update_test'),
    path('update',views.update, name='update'),
    path('test_database',views.test_database, name='test_database'),
    path('view_test',views.view_test, name='view_test'),
    path('view_score',views.view_score, name='view_score'),
    path('view_videos',views.view_videos,name='view_videos'),
    path('upload_videos',views.upload_videos,name='upload_videos'),
    path('delete_videos',views.delete_videos,name='delete_videos'),
    path('deleteView_videos',views.deleteView_videos,name='deleteView_videos'),
    path('python_home',views.python_home,name='python_home'),
    path('java_home',views.java_home,name='java_home'),
    path('SQL_home',views.SQL_home,name='SQL_home'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),


    #password_reset
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='registration/password_reset_request.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
         'password_reset_confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]