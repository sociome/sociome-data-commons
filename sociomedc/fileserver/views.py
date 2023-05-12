'''
Copyright (C) University of Chicago - All Rights Reserved

views.py defines the basic backend services of the sociome data commons.
'''

#django imports
from django.http import FileResponse
from django.shortcuts import render

#file imports
from fileserver.models import *
from fileserver.metadata import *

def index(request, new_dataset=False):
    '''index renders the main landing page of the sociome data commons
    '''

    if request.method == 'GET':
        return render(request, 'index.html', {'datasets': Dataset.objects.all()})

    if request.method == 'POST':
        search = request.POST.get('search', '')

        return render(request, 'index.html', {'datasets': findDatasets(search)})


def upload(request):
    '''upload serves and processes dataset uploadss
    '''

    #generates the metadata form from the dictionary
    metadata = do_form('../metadata')

    #serves the form
    if request.method == 'GET':
        return render(request, 'upload.html', {'metadata': metadata, 'error': False})

    #handles the form
    if request.method == 'POST':
        
        try:
            name = request.POST.get('name', '')
            desc = request.POST.get('desc', '')
            file = request.FILES.get('filename')
            new_dataset = createDataset(file, name, desc)

        except ValueError as e:
            return render(request, 'upload.html', {'metadata': metadata, 'error': True, 'message': str(e)})


        try:
            for key,value in request.POST.items():

                if 'metadata' in key:
                    key = key.split('_')[1]
                    addMetadata(new_dataset, key, value)

        except ValueError as e:
            return render(request, 'upload.html', {'metadata': metadata, 'error': True, 'message': str(e)})


        return index(request, True)


def dictionary(request):
    str = do_html('../metadata')
    return render(request, 'dictionary.html', {'metadata': str})

def dataset(request):
    if request.method == 'GET':
        uuid = request.GET.get('id')
        dataset = Dataset.objects.filter(uuid=uuid)
        client_ip = request.build_absolute_uri('/')

        metadata = Metadata.objects.filter(dataset = dataset[0]) 
        return render(request, 'dataset.html', {'dataset': dataset[0], 'clientip': client_ip, 'metadata': metadata})


def download(request):
    if request.method == 'GET':
        uuid = request.GET.get('id')
        dataset = Dataset.objects.get(uuid=uuid)
        filename = dataset.file.path
        response = FileResponse(open(filename, 'rb'))
        return response
