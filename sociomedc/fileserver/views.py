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
from sociomedc.settings import SERVER_URL, SERVER_ROOT

import os

import pandas as pd

def index(request):
    '''index renders the main about page
    '''

    return render(request, 'index.html', {})



def dataset_index(request, new_dataset=False):
    '''dataset_index renders the main landing page of the sociome data commons
    '''

    if request.method == 'GET':
        return render(request, 'list.html', {'datasets': Dataset.objects.all()})

    if request.method == 'POST':
        search = request.POST.get('search', '')

        if search == '':
            return render(request, 'list.html', {'datasets': Dataset.objects.all()})
        else:
            return render(request, 'list.html', {'datasets': findDatasets(search)})


def upload(request):
    '''
    Upload pushes a dataset into the repository
    :param request: HTTPRequest
    :return:
    '''

    #can only modify db locally forces us to version 
    #control catalog
    if not 'localhost' in SERVER_URL:
        render(request, 'index.html', {})

    metadata = do_form(SERVER_ROOT + '/metadata')

    if request.method == 'GET':
        return render(request, 'upload.html', {'metadata': metadata, 'error': False})


    if request.method == 'POST':

        name = request.POST.get('name')
        desc = request.POST.get('desc')
        file = request.POST.get('filename')
        data_dict = request.POST.get('datadict')

        new_dataset = Dataset(file=file, data_dict=data_dict, name=name,desc=desc)
        new_dataset.save()

        for key,value in request.POST.items():

            if 'metadata' in key:
                key = key.split('_')[1]
                m = Metadata(dataset=new_dataset, key=key, value=value)
                m.save()

        return dataset_index(request, True)


def notebook(request):
    '''
    Upload pushes a dataset into the repository
    :param request: HTTPRequest
    :return:
    '''

    #can only modify db locally forces us to version 
    #control catalog
    if not 'localhost' in SERVER_URL:
        render(request, 'index.html', {})

    if request.method == 'GET':
        uuid = request.GET.get('uuid')
        return render(request, 'notebook.html', {'uuid': uuid, 'error': False})

    if request.method == 'POST':

        name = request.POST.get('name')
        id = request.POST.get('id')
        file = request.FILES['file'].read()
        dataset = Dataset.objects.filter(uuid=id)[0]

        new_notebook = Notebook(dataset=dataset, name=name,html=file)
        new_notebook.save()

        return dataset_index(request, True)


def dictionary(request):
    '''Defines the data dictionary for the sociome data commons
    '''
    str = do_html(SERVER_ROOT + '/metadata')
    return render(request, 'dictionary.html', {'metadata': str})


def dataset(request):
    if request.method == 'GET':
        uuid = request.GET.get('id')
        dataset = Dataset.objects.filter(uuid=uuid)
        client_ip = SERVER_URL

        metadata = Metadata.objects.filter(dataset=dataset[0])

        notebook = [n.html[2:].replace("\\/", "/").encode().decode('unicode_escape').replace('Â','') for n in Notebook.objects.filter(dataset=dataset[0])]

        return render(request, 'dataset.html',
                      {'dataset': dataset[0], 'download': dataset[0].file,
                       'metadata': metadata, 'notebook': notebook})


def dataset_api(request, dataset_id):
    dataset = Dataset.objects.filter(uuid=dataset_id)
    data_file_extension = dataset[0].file.name.split('.')[-1].lower()

    if data_file_extension == 'zip':
        try:
            zip_file_data = dataset[0].file.read()

            # Create an in-memory file-like object for the zip file data
            in_memory_zip = io.BytesIO(zip_file_data)

            # Create the response with the zip file data
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = f'attachment'
            response.write(in_memory_zip.getvalue())

            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    elif data_file_extension == 'csv':
        try:
            file_path = dataset[0].file.path

            # Read the CSV data into a DataFrame
            df = pd.read_csv(file_path)

            # Convert DataFrame to JSON and return as a response
            data = df.to_dict(orient='records')
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)})

def download(request):
    if request.method == 'GET':
        uuid = request.GET.get('id')
        dataset = Dataset.objects.get(uuid=uuid)
        filename = dataset.file.path
        response = FileResponse(open(filename, 'rb'))
        return response
