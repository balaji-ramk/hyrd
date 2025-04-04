from django.urls import path
from . import views

app_name = 'employer'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:company_id>/jobs/', views.job_list, name='job_list'),
    path('companies/<int:company_id>/jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/select-candidates/', views.select_candidates, name='select_candidates'),
    path('companies/<int:company_id>/jobs/autofill/', views.job_autofill, name='job_autofill'),
]