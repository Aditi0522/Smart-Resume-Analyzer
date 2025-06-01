from django import forms
from .models import Resume, JobDescription

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ResumeUploadForm(forms.Form):
    name = forms.CharField(max_length=100)
    docfiles = MultipleFileField(label='Select a PDF file/files', required=True)

    def clean_docfiles(self):
        files = self.cleaned_data.get('docfiles')
        for f in files:
            if not f.name.lower().endswith('.pdf'):
                raise forms.ValidationError(f"{f.name} is not a PDF file.")
        return files

class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['description']