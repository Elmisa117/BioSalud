from django.urls import path
from .views_admin import dashboard_view, personal_list

urlpatterns = [
    path('', dashboard_view, name='admin_dashboard'),
    path('personal/', personal_list, name='personal_list'),
]
