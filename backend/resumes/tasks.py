from .utils import pdf2text, preprocess_text
from celery import shared_task
from time import sleep
from .models import Resume

@shared_task
def process_multiple_resume(resumeid):
    sleep(5)
    print(f'processing resume {resumeid}')
    resume = Resume.objects.get(id=resumeid)
    try:
        raw_text = pdf2text(resume.docs.path)
        clean_text = raw_text.replace('\x00','')
        resume.parsed_text = clean_text
        resume.status = 'completed'
        resume.save()

        tokens = preprocess_text(resume.parsed_text)
    except Exception as e:
        resume.parsed_text = f"Error: {str(e)}"
        resume.status = 'failed'

    return f"Resume {resumeid} processed"
    