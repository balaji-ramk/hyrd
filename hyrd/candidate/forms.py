from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    document = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Resume
        fields = ['document', 'name', 'email', 'phone', 'summary', 'skills', 'experience', 'education']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 