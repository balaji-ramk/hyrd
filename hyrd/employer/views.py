from django.shortcuts import render, redirect, get_object_or_404
import os
import tempfile
from .models import User, Company, Job, AppliedJob
from .forms import LoginForm, CompanyForm, JobForm
from .utils import extract_job_description, ResumeRanker
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
    
    # Check if we should clear the ranking results
    if request.GET.get('clear_ranking') == 'true':
        if 'ranked_candidates' in request.session:
            del request.session['ranked_candidates']
    
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

def rank_candidates(request, job_id):
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
    
    # Get candidates who applied for this job
    applications = AppliedJob.objects.filter(job=job).select_related('candidate__resume')
    
    # Prepare job data
    job_data = {
        "Job Title": job.title,
        "Job Summary": job.summary,
        "Responsibilities": job.responsibilities,
        "Requirements": {
            "Educational": job.educational_requirements,
            "Technical": job.technical_requirements,
            "Experience (Years of experience)": str(job.experience_years) if job.experience_years else "0"
        },
        "Preferred Qualifications": job.preferred_qualifications,
        "Location": job.location
    }
    
    # Prepare resume data for each candidate
    resumes_data = []
    for application in applications:
        candidate = application.candidate
        try:
            resume = candidate.resume
            if resume:
                # Convert resume fields to the expected format
                resume_data = {
                    "Basics": {
                        "Name": candidate.first_name + " " + candidate.last_name if candidate.last_name else candidate.first_name,
                        "Email": candidate.email,
                        "Phone": resume.phone,
                        "Summary": resume.summary
                    },
                    "Work": [],
                    "Education": [],
                    "Skills": []
                }
                
                # Parse experience text into work history
                if resume.experience:
                    # Simple parsing of experience text - this is a basic implementation
                    # In a real app, you'd want more sophisticated parsing
                    experience_blocks = resume.experience.split('\n\n')
                    for block in experience_blocks:
                        if block.strip():
                            lines = block.strip().split('\n')
                            if len(lines) >= 2:
                                position_company = lines[0].split(' at ')
                                position = position_company[0] if len(position_company) > 0 else ""
                                company = position_company[1] if len(position_company) > 1 else ""
                                
                                # Try to extract dates
                                dates = ""
                                start_date = ""
                                end_date = ""
                                for line in lines[1:]:
                                    if " - " in line and not line.startswith("•"):
                                        dates = line
                                        date_parts = dates.split(" - ")
                                        start_date = date_parts[0]
                                        end_date = date_parts[1] if len(date_parts) > 1 else "Present"
                                        break
                                
                                # Get highlights
                                highlights = []
                                for line in lines:
                                    if line.startswith("•"):
                                        highlights.append(line[1:].strip())
                                
                                # Create work entry
                                work_entry = {
                                    "Name": company,
                                    "Position": position,
                                    "Start Date": start_date,
                                    "End Date": end_date,
                                    "Summary": "",
                                    "Highlights": highlights
                                }
                                resume_data["Work"].append(work_entry)
                
                # Parse skills
                if resume.skills:
                    skills_lines = resume.skills.strip().split('\n')
                    for skill_line in skills_lines:
                        if ":" in skill_line:
                            skill_name, keywords = skill_line.split(":", 1)
                            keywords = [k.strip() for k in keywords.split(',')]
                            resume_data["Skills"].append({
                                "Name": skill_name.strip(),
                                "Keywords": keywords
                            })
                        else:
                            resume_data["Skills"].append({
                                "Name": skill_line.strip(),
                                "Keywords": []
                            })
                
                # Parse education
                if resume.education:
                    education_blocks = resume.education.split('\n\n')
                    for block in education_blocks:
                        if block.strip():
                            lines = block.strip().split('\n')
                            if lines:
                                institution = lines[0]
                                area = ""
                                degree = ""
                                start_date = ""
                                end_date = ""
                                
                                for i, line in enumerate(lines[1:], 1):
                                    if "in" in line and not line.startswith("•"):
                                        degree_parts = line.split(" in ")
                                        degree = degree_parts[0]
                                        area = degree_parts[1] if len(degree_parts) > 1 else ""
                                    elif " - " in line and not line.startswith("•"):
                                        date_parts = line.split(" - ")
                                        start_date = date_parts[0]
                                        end_date = date_parts[1] if len(date_parts) > 1 else ""
                                
                                education_entry = {
                                    "Institution": institution,
                                    "Area of Study": area,
                                    "Study Type": degree,
                                    "Start Date": start_date,
                                    "End Date": end_date
                                }
                                resume_data["Education"].append(education_entry)
                
                resumes_data.append(resume_data)
        except Exception as e:
            # If there's an error processing a resume, skip it
            print(f"Error processing resume for {candidate.email}: {str(e)}")
    
    # Initialize the resume ranker
    ranker = ResumeRanker()
    
    # Rank the resumes
    if resumes_data:
        ranked_results = ranker.rank_resumes(job_data, resumes_data)
        
        # Store the ranking results in the session for display
        request.session['ranked_candidates'] = ranked_results
        
        return redirect('employer:job_detail', job_id=job.id)
    else:
        # No valid resumes to rank
        return redirect('employer:job_detail', job_id=job.id)

