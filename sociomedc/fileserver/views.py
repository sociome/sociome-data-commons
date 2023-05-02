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

    if request.method == 'GET':
        return render(request, 'upload.html')

    if request.method == 'POST':

        name = request.POST.get('name')
        desc = request.POST.get('desc')
        file = request.FILES.get('filename')

        new_dataset = Dataset(file=file, name=name,desc=desc)
        new_dataset.save()

        return index(request, True)


def dataset(request):
    if request.method == 'GET':
        uuid = request.GET.get('id')
        dataset = Dataset.objects.filter(uuid=uuid)
        client_ip = str(request.META['REMOTE_ADDR']) 
        #print(client_ip)
        return render(request, 'dataset.html', {'dataset': dataset[0], 'clientip': client_ip})

