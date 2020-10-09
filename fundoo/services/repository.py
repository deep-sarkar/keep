from note.models import LabelMap, Note
from label.models import Label
from django.core.exceptions import ObjectDoesNotExist
from note.exceptions import LabelMappingException, NotesNotFoundError
from util.status import response_code

def add_label_id_from_label(labels, instance, user):
    for label in labels:
        try:
            single_label = Label.objects.get(name = label, user = user.id)
        except ObjectDoesNotExist:
            single_label = Label.objects.create(name = label, user = user)
        try:
            LabelMap.objects.create(label=single_label, note = instance)
        except Exception:
            raise LabelMappingException(code=417, msg=response_code[417])

def edit_label_id_from_label(labels, instance, user):
    for label in labels:
        try:
            single_label = Label.objects.get(name = label, user = user.id)
        except ObjectDoesNotExist:
            single_label = Label.objects.create(name = label, user = user)
        try:
            LabelMap.objects.get(label=single_label, note = instance)
        except ObjectDoesNotExist:
            LabelMap.objects.create(label=single_label, note = instance)

def get_all_note(user_id):
    try:
        query = '''SELECT * 
                    FROM note_note 
                    WHERE (trash = false) and (archive = false) and (user_id=%s) 
                    ORDER BY pin desc, id desc''' % user_id
        notes = Note.objects.raw(query)
        return notes
    except Exception:
        raise NotesNotFoundError(409, response_code[409])

def get_all_trash_note(user_id):
    try:
        query = '''SELECT * 
                    FROM note_note 
                    WHERE (trash = true) and (user_id=%s) 
                    ORDER BY pin desc, id desc''' % user_id
        notes = Note.objects.raw(query)
        return notes
    except Exception:
        raise NotesNotFoundError(409, response_code[409])