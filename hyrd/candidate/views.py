from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import os
import tempfile
from employer.models import User, Job, AppliedJob
from .models import Resume
from .forms import ResumeForm
from employer.utils import extract_resume

def login_required_candidate(view_func):
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('employer:login')
        
        try:
            user = User.objects.get(id=user_id)
            if user.is_employer:
                return redirect('employer:company_list')
        except User.DoesNotExist:
            return redirect('employer:login')
        
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_candidate
def index(request):
    user = User.objects.get(id=request.session.get('user_id'))
    jobs = Job.objects.all()
    applied_jobs = AppliedJob.objects.filter(candidate=user).values_list('job_id', flat=True)
    
    return render(request, 'candidate/job_list.html', {
        'jobs': jobs,
        'applied_jobs': applied_jobs,
        'user': user
    })

@login_required_candidate
def apply_job(request, job_id):
    user = User.objects.get(id=request.session.get('user_id'))
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    if not AppliedJob.objects.filter(job=job, candidate=user).exists():
        # Check if user has a resume
        if not Resume.objects.filter(user=user).exists():
            return redirect('candidate:upload_resume')
        
        # Create application
        AppliedJob.objects.create(job=job, candidate=user, status='Applied')
    
    return redirect('candidate:index')

@login_required_candidate
def my_applications(request):
    user = User.objects.get(id=request.session.get('user_id'))
    applications = AppliedJob.objects.filter(candidate=user).select_related('job')
    
    return render(request, 'candidate/my_applications.html', {
        'applications': applications,
        'user': user
    })

@login_required_candidate
def upload_resume(request):
    user = User.objects.get(id=request.session.get('user_id'))
    
    # Check if user already has a resume
    try:
        resume = Resume.objects.get(user=user)
        form = ResumeForm(instance=resume)
    except Resume.DoesNotExist:
        resume = None
        form = ResumeForm()
    
    if request.method == 'POST':
        if resume:
            form = ResumeForm(request.POST, request.FILES, instance=resume)
        else:
            form = ResumeForm(request.POST, request.FILES)
        
        if form.is_valid():
            resume_obj = form.save(commit=False)
            resume_obj.user = user
            resume_obj.save()
            return redirect('candidate:my_applications')
    
    return render(request, 'candidate/upload_resume.html', {
        'form': form,
        'user': user,
        'resume': resume
    })


def resume_autofill(request):
    if request.method != 'POST' or 'document' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file provided'})
    
    try:
        pdf_file = request.FILES['document']
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        resume_data = extract_resume(temp_path)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        # Check if resume_data is None or not a dictionary
        if resume_data is None or not isinstance(resume_data, dict):
            return JsonResponse({
                'success': False,
                'error': 'Failed to extract data from resume'
            })
        
        # Extract data from the resume with proper error handling
        basics = resume_data.get('basics', {}) or {}
        skills_data = resume_data.get('skills', []) or []
        work_data = resume_data.get('work', []) or []
        education_data = resume_data.get('education', []) or []
        
        # Format skills
        skills_text = ""
        if isinstance(skills_data, list):
            for skill in skills_data:
                if isinstance(skill, dict):
                    skill_name = skill.get('name', '')
                    keywords = skill.get('keywords', [])
                    if skill_name:
                        skills_text += f"{skill_name}"
                        if keywords and isinstance(keywords, list):
                            skills_text += f": {', '.join(keywords)}"
                        skills_text += "\n"
        
        # Format work experience
        experience_text = ""  # Initialize the variable
        if isinstance(work_data, list):
            for work in work_data:
                if isinstance(work, dict):
                    company = work.get('name', '')
                    position = work.get('position', '')
                    start_date = work.get('start_date', '')
                    end_date = work.get('end_date', '')
                    summary = work.get('summary', '')
                    highlights = work.get('highlights', [])
                    
                    if company and position:
                        experience_text += f"{position} at {company}\n"
                        if start_date or end_date:
                            experience_text += f"{start_date} - {end_date}\n"
                        if summary:
                            experience_text += f"{summary}\n"
                        if highlights and isinstance(highlights, list):
                            for highlight in highlights:
                                experience_text += f"• {highlight}\n"
                        experience_text += "\n"
        
        # Format education
        education_text = ""
        if isinstance(education_data, list):
            for edu in education_data:
                if isinstance(edu, dict):
                    institution = edu.get('institution', '')
                    area = edu.get('area_of_study', '') or edu.get('area', '')
                    degree = edu.get('study_type', '')
                    start_date = edu.get('start_date', '')
                    end_date = edu.get('end_date', '')
                    score = edu.get('score', '')
                    courses = edu.get('courses', [])
                    
                    if institution:
                        education_text += f"{institution}\n"
                        if degree and area:
                            education_text += f"{degree} in {area}\n"
                        elif degree:
                            education_text += f"{degree}\n"
                        elif area:
                            education_text += f"{area}\n"
                        if start_date or end_date:
                            education_text += f"{start_date} - {end_date}\n"
                        if score:
                            education_text += f"GPA/Score: {score}\n"
                        if courses and isinstance(courses, list):
                            education_text += "Courses:\n"
                            for course in courses:
                                education_text += f"• {course}\n"
                        education_text += "\n"
        
        # Get summary from basics
        summary = basics.get('summary', '') if isinstance(basics, dict) else ''
        
        # Prepare response data
        fields = {
            'name': basics.get('name', '') if isinstance(basics, dict) else '',
            'email': basics.get('email', '') if isinstance(basics, dict) else '',
            'phone': basics.get('phone', '') if isinstance(basics, dict) else '',
            'summary': summary,
            'skills': skills_text,
            'experience': experience_text,
            'education': education_text
        }
        
        return JsonResponse({
            'success': True,
            'fields': fields
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
