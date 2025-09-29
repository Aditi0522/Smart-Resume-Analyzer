from django.shortcuts import render,redirect
from .forms import ResumeUploadForm, JobDescriptionForm, MatchFilterForm
from .models import Resume, JobDescription, MatchScores
from django.utils import timezone
from .tasks import process_multiple_resume, process_job_description
from django.views.decorators.http import require_GET

def upload_success(request):
    message = request.session.pop('upload_msg', None)
    return render(request, 'resumes/uploaded.html', {'upload_msg': message})

def upload_resumes(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST,request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('docfiles')
            name = form.cleaned_data['name']
            for f in files:
                resume=Resume.objects.create(
                    name=name,
                    docs=f,
                    date_uploaded=timezone.now(),
                    status='pending'
                )
                #trigger celery task here
                process_multiple_resume.delay(resume.id)
            request.session['upload_msg']=f"{len(files)} resume(s) uploaded and job description saved."
            return redirect('uploaded')
    else:
        form=ResumeUploadForm()
    return render(request, 'resumes/upload_resumes.html', {'form':form})

def upload_job(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job = form.save()
            #trigger celery task here
            process_job_description.delay(job.id)
            request.session['upload_msg'] = "Job description uploaded"
            return redirect('uploaded')
    else:
            form = JobDescriptionForm()

    return render(request, 'resumes/upload_job.html', {'form':form})

def matches_view(request):
    form = MatchFilterForm(request.GET or None)
    context = {'form': form}
    matches = []
    single_match = None

    if form.is_valid():
        job_title = form.cleaned_data.get('job_title')
        resume_name = form.cleaned_data.get('resume_name')
        top_n = form.cleaned_data.get('top_n')
        
        print("Form Valid:", form.is_valid())
        print("Job Title:", job_title)
        print("Resume Name:", resume_name)
        print("Top N:", top_n)

        job = resume = None

        try:
            if job_title:
                job = JobDescription.objects.get(title__iexact=job_title)
            if resume_name:
                resume = Resume.objects.get(name__iexact=resume_name)
            
            if resume and resume.status != 'completed':
                context['error'] = f"Resume '{resume.name}' is still being processed. Try again later."
                return render(request, 'resumes/matches.html', context)

            if job and resume:
                print("Fetching match for job and resume...")
                try:

                    match = MatchScores.objects.get(job_id=job, resume_id=resume)
                    context['single_match'] = {
                        'score': match.score,
                        'resume_id': match.resume_id.id,
                        'resume_name': match.resume_id.name,
                        'job_id': match.job_id.id,
                        'job_title': match.job_id.title,
                    }
                except MatchScores.DoesNotExist:
                    context['error'] = "No match data available for the given inputs."

            elif job:
                print("Filtering MatchScores for job only...")

                qs = MatchScores.objects.filter(job_id=job).order_by('-score')
                if top_n:
                    qs = qs[:top_n]
                context['matches'] = [
                    {'resume_id': m.resume_id.id, 'resume_name': m.resume_id.name, 'score': m.score, 'job_title': job.title}
                    for m in qs
                ]
                if not context['matches']:
                    context['error'] = "No resumes matched for this job."

            elif resume:
                print("Filtering MatchScores for resune only...")

                qs = MatchScores.objects.filter(resume_id=resume).order_by('-score')
                if top_n:
                    qs = qs[:top_n]
                context['matches'] = [
                    {'job_id': m.job_id.id, 'job_title': m.job_id.title, 'score': m.score, 'resume_name': resume.name}
                    for m in qs
                ]
                if not context['matches']:
                    context['error'] = "No job matches found for this resume."
            
            elif top_n:
                qs = MatchScores.objects.all().order_by('-score')[:top_n]
                context['matches'] = [
                    {
                        'resume_id': m.resume_id.id,
                        'resume_name': m.resume_id.name,
                        'job_id': m.job_id.id,
                        'job_title': m.job_id.title,
                        'score': m.score,
                    } for m in qs
                ]
                if not context['matches']:
                    context['error'] = "No match data found."

            else:
                context ['error'] = "Please provide atleast one filter"

        except (JobDescription.DoesNotExist, Resume.DoesNotExist, MatchScores.DoesNotExist):
            context['error'] = "No match found."

        

    else:
         context['error'] = "Invalid form submission."

    return render(request, 'resumes/matches.html', context)
