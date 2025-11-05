from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('create-mess/', views.create_mess, name='create_mess'),
    path('join-mess/', views.join_mess, name='join_mess'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mess/<int:mess_id>/dashboard/', views.mess_dashboard, name='mess_dashboard'),
    path('mess/<int:mess_id>/member-dashboard/', views.member_dashboard, name='member_dashboard'),
    
    path('mess/<int:mess_id>/manage-members/', views.manage_members, name='manage_members'),
    path('mess/<int:mess_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('mess/<int:mess_id>/update-accounts/', views.update_accounts, name='update_accounts'),
    path('mess/<int:mess_id>/add-meal/', views.add_meal, name='add_meal'),
    path('mess/<int:mess_id>/add-expense/', views.add_expense, name='add_expense'),
    path('mess/<int:mess_id>/add-deposit/', views.add_deposit, name='add_deposit'),
    path('mess/<int:mess_id>/view-reports/', views.view_reports, name='view_reports'),
    path('mess/<int:mess_id>/download-report-pdf/', views.download_report_pdf, name='download_report_pdf'),
    path('mess/<int:mess_id>/role-change/', views.role_change, name='role_change'),
    
    path('member/mess-list/', views.member_mess_list, name='member_mess_list'),
    path('member/mess/<int:mess_id>/members/', views.member_members, name='member_members'),
    
    path('mess/<int:mess_id>/messages/', views.messages_view, name='manager_messages'),
    path('member/mess/<int:mess_id>/messages/', views.messages_view, name='member_messages'),
    
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
]