from django.db import models

# Create your models here.
class DataRecord(models.Model):
    data = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)