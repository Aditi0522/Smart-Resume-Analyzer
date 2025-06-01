from django.db import models
from django.utils import timezone 
from django.core.validators import FileExtensionValidator

class Resume(models.Model):
    STATUS_CHOICES=(
     ('pending','PENDING'),
     ('completed','Completed'),
     ('failed','Failed'),  
    )
    docs = models.FileField(upload_to='uploads/%Y/%m/%d/',blank=False,validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    date_uploaded = models.DateTimeField(default=timezone.now )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    parsed_text = models.TextField(blank=True,null=True)
    
class JobDescription(models.Model):
    description = models.TextField()

class MatchScores(models.Model):
    resume_id = models.ForeignKey('Resume', on_delete=models.CASCADE)
    job_id = models.ForeignKey('JobDescription', on_delete=models.CASCADE)
    score = models.FloatField()

    class Meta:
        unique_together = ('resume_id', 'job_id')
