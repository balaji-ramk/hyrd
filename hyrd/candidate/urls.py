from django.urls import path
from . import views

app_name = 'candidate'

urlpatterns = [
    path('', views.index, name='index'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('applications/', views.my_applications, name='my_applications'),
    path('resume/upload/', views.upload_resume, name='upload_resume'),
    path('resume/autofill/', views.resume_autofill, name='resume_autofill'),
]
