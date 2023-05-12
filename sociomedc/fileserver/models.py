'''
Copyright (C) University of Chicago - All Rights Reserved

models.py describes the database tables that back the sociome data commons. It also defines the basic API 
subroutines that allow for querying and modifying these tables.
'''

from django.db import models
import uuid


class Dataset(models.Model):
    '''Defines the basic structure for handling and serving uploaded datasets to the data commons.

    Attributes:
        file: a FileField that represents an actual data contents of a sociome asset
        name: a CharField unique identifier for a dataset
        desc: a CharField a searchable description for a dataset, main difference between this and meta data is searchability
        uuid: a CharField an obfuscated uuid for a dataset
    '''

    #path to an ordinary file on disk
    file = models.FileField()

    #an identifying name
    name = models.CharField(max_length=128, primary_key=True)

    #an identifying description
    desc = models.CharField(max_length=1024)

    #unique identifier
    uuid = models.CharField(max_length=32)


    '''File creation errors
    '''
    BLANK_NAME_ERROR = "The dataset name cannot be blank."
    NAME_FORMAT_ERROR = "The dataset name must not contain any spaces, e.g., chicago_crime."
    DUPLICATE_NAME_ERROR = "Another dataset with this name exists."
    FILE_FORMAT_ERROR = "The dataset is missing or not properly formatted."


    def save(self, *args, **kwargs):
        self.uuid = uuid.uuid4()
        super(Dataset, self).save(*args, **kwargs)


def createDataset(file, name, desc):
    '''createDataset adds a new dataset to the sociome after validating the inputs
    '''
    if len(name) == 0:
        raise ValueError(Dataset.BLANK_NAME_ERROR)

    if len(name.split()) > 1:
        raise ValueError(Dataset.NAME_FORMAT_ERROR)

    if Dataset.objects.filter(name = name).count() > 0:
        raise ValueError(Dataset.DUPLICATE_NAME_ERROR)

    if file is None:
        raise ValueError(Dataset.FILE_FORMAT_ERROR)

    new_dataset = Dataset(file=file, name=name,desc=desc)
    new_dataset.save()

    return new_dataset


def findDatasets(str=""):
    '''findDatasets returns a subset of relevant datasets for a user
    '''
    rtn = []
    
    str = str.lower()

    for dataset in Dataset.objects.all():

        if str == "":
            rtn.append(dataset)
            continue

        for word in str.split():
            if word in dataset.name.lower() or word in dataset.desc.lower():
                rtn.append(dataset)

    return rtn



class Metadata(models.Model):
    '''Metadata stores associates metadata fields with the datasets in a simple key-value model
    '''
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    key = models.CharField(max_length=1024)
    value = models.CharField(max_length=1024)

    '''File creation errors
    '''
    METADATA_ERROR = 'The key of this metadata field is blank. '

def addMetadata(dataset, key, value):
    '''addMetadata associates a key-value pair with a dataset
    '''

    if len(key) == 0 or dataset is None:
        raise ValueError(Metadata.METADATA_ERROR)

    if Metadata.objects.filter(dataset = dataset, key = key).count() > 0:
        md_obj = Metadata.objects.filter(dataset = dataset, key = key)[0]
        md_obj.key = key
        md_obj.value = value
        md_obj.save()
    else:
        m = Metadata(dataset=dataset, key=key, value=value)
        m.save()


