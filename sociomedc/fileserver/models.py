from django.db import models
import uuid

class Dataset(models.Model):
    '''Defines the basic structure for handling and serving files
    '''
    #path to an ordinary file on disk
    file = models.FileField(upload_to ='uploads/')

    #an identifying name
    name = models.CharField(max_length=128)

    #an identifying description
    desc = models.CharField(max_length=1024)

    #unique identifier
    uuid = models.CharField(max_length=32)

    def save(self, *args, **kwargs):
        self.uuid = uuid.uuid4()
        super(Dataset, self).save(*args, **kwargs)


class Metadata(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    key = models.CharField(max_length=1024)
    value = models.CharField(max_length=1024)
