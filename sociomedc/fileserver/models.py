from django.db import models
import uuid

'''Defines the basic structure for handling and serving files
'''
class Dataset(models.Model):
    file = models.FileField(upload_to ='uploads/')
    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=1024)
    uuid = models.CharField(max_length=32)

    def save(self, *args, **kwargs):
        self.uuid = uuid.uuid4()
        super(Dataset, self).save(*args, **kwargs)