from django import forms
from .models import Company, Job, User

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class JobForm(forms.ModelForm):
    document = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Job
        fields = [
            'title', 'about_company', 'summary', 'responsibilities',
            'educational_requirements', 'technical_requirements',
            'experience_years', 'preferred_qualifications',
            'location', 'compensation', 'document'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'about_company': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'educational_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'technical_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'preferred_qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'compensation': forms.TextInput(attrs={'class': 'form-control'}),
        }
