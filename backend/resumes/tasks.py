from .utils import pdf2text, preprocess_text, compute_cosine_similarity
from celery import shared_task
from time import sleep
from .models import Resume, JobDescription,MatchScores

@shared_task
def process_multiple_resume(resumeid):
    sleep(10)
    print(f'processing resume {resumeid}')
    resume = Resume.objects.get(id=resumeid)
    try:
        raw_text = pdf2text(resume.docs.path)
        clean_text = raw_text.replace('\x00','')
        resume.parsed_text = clean_text
        resume.status = 'completed'
        resume.save()

        resume_text_tokens = preprocess_text(resume.parsed_text)
        
        for job in JobDescription.objects.all():
            job_tokens = preprocess_text(job.description)
            score = compute_cosine_similarity(resume_text_tokens, job_tokens)
            MatchScores.objects.update_or_create(
                resume_id = resume,
                job_id=job,
                defaults= {'score':score}
            )
    except Exception as e:
        resume.parsed_text = f"Error: {str(e)}"
        resume.status = 'failed'

    return f"Resume {resumeid} processed"
    

@shared_task
def process_job_description(jobid):
    sleep(10)
    job = JobDescription.objects.get(id=jobid)
    job_tokens = preprocess_text(job.description)

    for resume in Resume.objects.all():
        try:
            if resume.parsed_text:
                resume_tokens = preprocess_text(resume.parsed_text)
                score = compute_cosine_similarity(resume_tokens, job_tokens)
                MatchScores.objects.update_or_create(
                    resume_id=resume,
                    job_id=job,
                    defaults={'score': score}
                )
        except Exception as e:
            print(f"[ERROR] Failed to match Resume ID {resume.id} with Job ID {job.id}: {e}")
            resume.status = 'failed'
            resume.save()
    return f"Job {jobid} processed"