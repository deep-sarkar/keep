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