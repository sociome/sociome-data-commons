from django.db import models
import uuid

class Dataset(models.Model):
    '''Defines the basic structure for handling and serving files
    '''
    file = models.URLField(max_length=200)
    data_dict = models.URLField(max_length=200)

    #an identifying name
    name = models.CharField(max_length=128)

    #an identifying description
    desc = models.CharField(max_length=1024)

    #unique identifier
    uuid = models.CharField(max_length=32)

    def save(self, *args, **kwargs):
        self.uuid = uuid.uuid4()
        super(Dataset, self).save(*args, **kwargs)


#validate
def validateUpload(name, desc):
    if len(name.split()) > 1:
        raise ValueError("The dataset name must not contain any spaces, e.g., chicago_crime")
    return None


class Metadata(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    key = models.CharField(max_length=1024)
    value = models.CharField(max_length=1024)


def get_power_set(s):
  power_set=[[]]
  for elem in s:
    # iterate over the sub sets so far
    for sub_set in power_set:
      # add a new subset consisting of the subset at hand added elem to it
      # effectively doubling the sets resulting in the 2^n sets in the powerset of s.
      power_set=power_set+[list(sub_set)+[elem]]
  return power_set


'''
search algoithm methodology:
- split search_phrase into search_terms
- for each term in search_terms:
    - a dataset gets 3 points if the term is in the dataset name
    - a dataset gets 1 point if the term is in the dataset description or metadata
- for each dataset with points, add up all the points in a dictionary
- return a list of datasets from the search in order of descending points
'''
def findDatasets(search_phrase):
    '''findDatasets returns a subset of relevant datasets for a user
    '''
    if search_phrase == None:
        return []

    # if the search term is separated by spaces, split into individual words
    terms = search_phrase.split()

    results = dict()

    for term in terms:
        name_match = Dataset.objects.filter(name__contains=term)
        for dataset in name_match:
            if dataset.name not in results.keys():
                results[dataset.name] = 3
            else:
                results[dataset.name] += 3

        desc_match = Dataset.objects.filter(desc__contains=term)
        for dataset in desc_match:
            if dataset.name not in results.keys():
                results[dataset.name] = 1
            else:
                results[dataset.name] += 1

        meta_match = Metadata.objects.filter(value__contains=term)
        for metadata in meta_match:
            try:
                dataset = metadata.dataset
                if dataset.name not in results.keys():
                    results[dataset.name] = 1
                else:
                    results[dataset.name] += 1
            except:
                continue;

    sorted_results = sorted(results.items(), key=lambda x:x[1], reverse=True)

    dataset_list = []
    for key, val in sorted_results:
        dataset_list.append(Dataset.objects.filter(name = key)[0])

    return dataset_list


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


