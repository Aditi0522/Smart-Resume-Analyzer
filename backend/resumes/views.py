from django.shortcuts import render,redirect
from .forms import ResumeUploadForm, JobDescriptionForm
from .models import Resume, JobDescription, MatchScores
from django.utils import timezone
from django.contrib import messages
from .tasks import process_multiple_resume


def upload_success(request):
    message = request.session.pop('upload_msg', None)
    return render(request, 'resumes/uploaded.html', {'upload_msg': message})

def main(request):
    if request.method == 'POST':
        form_1 = ResumeUploadForm(request.POST,request.FILES)
        form_2 = JobDescriptionForm(request.POST)
        if form_1.is_valid() and form_2.is_valid():
            job = form_2.save()
            files = request.FILES.getlist('docfiles')
            name = form_1.cleaned_data['name']
            for f in files:
                resume=Resume.objects.create(
                    docs=f,
                    date_uploaded=timezone.now(),
                    status='pending'
                )
                #trigger celery task here
                process_multiple_resume.delay(resume.id)
            request.session['upload_msg']=f"{len(files)} resume(s) uploaded and job description saved."
            return redirect('uploaded')
    else:
        form_1=ResumeUploadForm()
        form_2=JobDescriptionForm()
    return render(request, 'resumes/main.html', {'form1':form_1, 'form2':form_2})


