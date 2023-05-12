'''views.py defines the http services provided by the sociome data commons
'''

from django.shortcuts import render
from fileserver.models import *
from fileserver.metadata import *

# Create your views here.
def index(request, new_dataset=False):
    return render(request, 'index.html', {'datasets': Dataset.objects.all()})


def dictionary(request):
    str = do_html('../metadata')
    return render(request, 'dictionary.html', {'metadata': str})


def upload(request):

    metadata = do_form('../metadata')

    if request.method == 'GET':
        return render(request, 'upload.html', {'metadata': metadata, 'error': True})


    if request.method == 'POST':

        name = request.POST.get('name')
        desc = request.POST.get('desc')
        file = request.FILES.get('filename')


        try:
            validateUpload(name, desc)
        except ValueError as e:
            return render(request, 'upload.html', {'metadata': metadata, 'error': True, 'message': str(e)})


        new_dataset = Dataset(file=file, name=name,desc=desc)
        new_dataset.save()


        for key,value in request.POST.items():

            if 'metadata' in key:
                key = key.split('_')[1]
                m = Metadata(dataset=new_dataset, key=key, value=value)
                m.save()

        return index(request, True)


def dataset(request):
    if request.method == 'GET':
        uuid = request.GET.get('id')
        dataset = Dataset.objects.filter(uuid=uuid)
        client_ip = str(request.META['REMOTE_ADDR'])

        metadata = Metadata.objects.filter(dataset = dataset[0]) 
        return render(request, 'dataset.html', {'dataset': dataset[0], 'clientip': client_ip, 'metadata': metadata})

