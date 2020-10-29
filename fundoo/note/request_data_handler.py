from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

def fetch_collaborator(request):
    try:
        collaborators = request.data.get('collaborators')
        return collaborators
    except KeyError:
        return None

def fetch_label(request):
    try:
        labels = request.data.get('labels')
        return labels
    except KeyError:
        return None

def fetch_reminder(request):
    try:
        rem = request.data.get('reminder')
        return rem
    except KeyError:
        return None

def save_image(request):
    try:
        image = request.FILES['image']
        name = str(request.user.id) + image.name 
        with default_storage.open(name , 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        request.data['image'] = name
        return name
    except Exception as e:
        return None