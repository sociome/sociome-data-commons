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

        return render(request, 'list.html', {'datasets': findDatasets(search)})


#I think we need to fix this
def upload(request):
    '''
    Upload pushes a dataset into the repository
    :param request: HTTPRequest
    :return:
    '''

    metadata = do_form(SERVER_ROOT + '/metadata')

    if request.method == 'GET':
        return render(request, 'upload.html', {'metadata': metadata, 'error': False})


    if request.method == 'POST':

        name = request.POST.get('name')
        desc = request.POST.get('desc')
        file = request.FILES.get('filename')
        if len(request.FILES) > 1:
            data_dict = request.FILES.get('data_dict')
            data_dict_exists = True
        else:
            data_dict_exists = False
            data_dict = None


        try:
            validateUpload(name, desc)
        except ValueError as e:
            return render(request, 'upload.html', {'metadata': metadata, 'error': True, 'message': str(e)})


        new_dataset = Dataset(file=file, data_dict=data_dict, data_dict_exists=data_dict_exists, name=name,desc=desc)
        new_dataset.save()


        for key,value in request.POST.items():

            if 'metadata' in key:
                key = key.split('_')[1]
                m = Metadata(dataset=new_dataset, key=key, value=value)
                m.save()

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

        data_dict_exists = dataset[0].data_dict_exists

        if data_dict_exists:
            dict_file_extension = dataset[0].data_dict.name.split('.')[-1].lower()
        else:
            dict_file_extension = None

        pdf_file_extensions = ['pdf']
        table_file_extensions = ['csv', 'xlsx']

        if dict_file_extension in table_file_extensions:
            if dict_file_extension == 'xlsx':
                df = pd.read_excel(dataset[0].data_dict.path)
                table_html = df.to_html(classes='table table-bordered table-hover')
            else:
                df = pd.read_csv(dataset[0].data_dict.path)
                table_html = df.to_html(classes='table table-bordered table-hover')
        else:
            table_html = None

        # data_file_extension = dataset[0].file.name.split('.')[-1].lower()
        # if data_file_extension == 'csv':
        #     extension_code = 1
        #     file_name = None
        # elif data_file_extension == 'zip':
        #     extension_code = 2
        #     file_name = os.path.basename(dataset[0].file.name).split(".")[0]
        # else:
        #     extension_code = 0
        #     file_name = None

        metadata = Metadata.objects.filter(dataset=dataset[0])
        
        # 0.0.1_hanging_on_chicago_assessments took out: 'file_name': file_name, 'extension_code': extension_code,
        return render(request, 'dataset.html',
                      {'dataset': dataset[0], 
                       'clientip': client_ip, 'table_html': table_html,
                       'metadata': metadata, 'pdf_file_extensions': pdf_file_extensions,
                       'table_file_extensions': table_file_extensions, 'dict_file_extension': dict_file_extension})


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
