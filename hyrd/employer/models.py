from django.db import models
# from django.contrib.auth.models import User

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100) 
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_employer = models.BooleanField(default=False)
    candidate_id = models.CharField(max_length=50, blank=True, null=True)
    # user_id = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return self.email

class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    job_id = models.CharField(max_length=50, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    about_company = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    educational_requirements = models.TextField(blank=True)
    technical_requirements = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    preferred_qualifications = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    compensation = models.CharField(max_length=100, blank=True)
    document = models.FileField(upload_to='job_documents/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"

class AppliedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='Applied')  # Status: Applied, Interview, Rejected, etc.

    def __str__(self):
        return f"{self.candidate.first_name} applied for {self.job.title}"

class EmployeeJobRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employer_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.user.email} - {self.job.title}"
