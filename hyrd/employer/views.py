from django.shortcuts import render, redirect, get_object_or_404
import os
import tempfile
from .models import User, Company, Job, AppliedJob
from .forms import LoginForm, CompanyForm, JobForm
from .utils import extract_job_description
from django.http import JsonResponse

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email, password=password)
                request.session['user_id'] = user.id
                if user.is_employer:
                    return redirect('employer:company_list')
                else:
                    return redirect('candidate:index')
            except User.DoesNotExist:
                form.add_error(None, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'employer/login.html', {'form': form})

def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('employer:login')

def company_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('employer:login')
    
    try:
        user = User.objects.get(id=user_id)
        if not user.is_employer:
            return redirect('employer:login')
    except User.DoesNotExist:
        return redirect('employer:login')
    
    companies = Company.objects.all()
    return render(request, 'employer/company_list.html', {
        'companies': companies,
        'user': user
    })

def company_create(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('employer:login')
    
    try:
        user = User.objects.get(id=user_id)
        if not user.is_employer:
            return redirect('employer:login')
    except User.DoesNotExist:
        return redirect('employer:login')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employer:company_list')
    else:
        form = CompanyForm()
    
    return render(request, 'employer/company_form.html', {
        'form': form,
        'user': user
    })

def job_list(request, company_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('employer:login')
    
    try:
        user = User.objects.get(id=user_id)
        if not user.is_employer:
            return redirect('employer:login')
    except User.DoesNotExist:
        return redirect('employer:login')
    
    company = get_object_or_404(Company, id=company_id)
    jobs = Job.objects.filter(company=company)
    
    return render(request, 'employer/job_list.html', {
        'company': company,
        'jobs': jobs,
        'user': user
    })

def job_create(request, company_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('employer:login')
    
    try:
        user = User.objects.get(id=user_id)
        if not user.is_employer:
            return redirect('employer:login')
    except User.DoesNotExist:
        return redirect('employer:login')
    
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.save()
            return redirect('employer:job_list', company_id=company.id)
    else:
        form = JobForm()
    
    return render(request, 'employer/job_form.html', {
        'form': form,
        'company': company,
        'user': user
    })

def job_detail(request, job_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('employer:login')
    
    try:
        user = User.objects.get(id=user_id)
        if not user.is_employer:
            return redirect('employer:login')
    except User.DoesNotExist:
        return redirect('employer:login')
    
    job = get_object_or_404(Job, id=job_id)
    
    # Get real candidates who applied for this job
    applied_candidates = AppliedJob.objects.filter(job=job).select_related('candidate')
    
    return render(request, 'employer/job_detail.html', {
        'job': job,
        'candidates': applied_candidates,
        'user': user
    })

def select_candidates(request, job_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('employer:login')
    
    try:
        user = User.objects.get(id=user_id)
        if not user.is_employer:
            return redirect('employer:login')
    except User.DoesNotExist:
        return redirect('employer:login')
    
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        selected_candidates = request.POST.getlist('selected_candidates')
        new_status = request.POST.get('status', 'Applied')
        
        if selected_candidates:
            # Update status for selected candidates
            AppliedJob.objects.filter(
                job=job, 
                candidate_id__in=selected_candidates
            ).update(status=new_status)
            
        return redirect('employer:job_detail', job_id=job.id)
    
    return redirect('employer:job_detail', job_id=job.id)

def job_autofill(request, company_id):
    if request.method != 'POST' or 'document' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file provided'})
    try:
        pdf_file = request.FILES['document']
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        job_data = extract_job_description(temp_path)
        # Clean up the temporary file
        os.unlink(temp_path)
        
        # Prepare the response data with proper type checking
        fields = {
            'title': job_data.get('job_title', ''),
            'about_company': job_data.get('about_the_company', ''),
            'summary': job_data.get('job_summary', ''),
            'responsibilities': '\n'.join(job_data.get('responsibilities', []) if isinstance(job_data.get('responsibilities'), list) else []),
            'educational_requirements': job_data.get('requirements', {}).get('educational', ''),
            'technical_requirements': job_data.get('requirements', {}).get('technical', ''),
            'preferred_qualifications': '\n'.join(job_data.get('preferred_qualifications', []) if isinstance(job_data.get('preferred_qualifications'), list) else []),
            'location': job_data.get('location', ''),
            'compensation': job_data.get('compensation', '')
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

