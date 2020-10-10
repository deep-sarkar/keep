from note.models import LabelMap, Note, UserMap
from label.models import Label
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from note.exceptions import ( LabelMappingException, 
                              NotesNotFoundError, 
                              LabelsNotFoundError, 
                              CollaboratorMappingException,
                              )
from util.status import response_code

def add_label_id_from_label(labels, instance, user):
    '''
    input:  labels   => list of string,
            instance => Note object instance,
            user     => request.user
    output: mapped list of label id to perticular note by create new relation
    error : Lable mapping exception
    '''
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
    '''
    input:  labels   => list of string,
            instance => Note object instance,
            user     => request.user
    output: mapped list of label id to perticular note by create new relation or by existing relation
    error : ObjectDoesNotExist
    '''
    for label in labels:
        try:
            single_label = Label.objects.get(name = label, user = user.id)
        except ObjectDoesNotExist:
            single_label = Label.objects.create(name = label, user = user)
        try:
            LabelMap.objects.get(label=single_label, note = instance)
        except ObjectDoesNotExist:
            LabelMap.objects.create(label=single_label, note = instance)

def add_collaborator_id_from_collaborator(collaborators, instance, user):
    '''
    input:  collaborators => list of string,
            instance      => Note object instance,
            user          => request.user
    output: mapped list of user id to perticular note by create new relation
    error : ObjectDoesNotExist, CollaboratorMappingException
    '''
    invalid_user = []
    for collaborator in collaborators:
        try:
            single_user = User.objects.get(username = collaborator)
        except ObjectDoesNotExist:
            invalid_user.append(collaborator)
        try:
            UserMap.objects.get_or_create(user = single_user, note = instance)
        except Exception as e:
            raise CollaboratorMappingException(code=418, msg=response_code[418])
    return invalid_user

def get_single_note(id, user_id):
    '''
    input : id      => requested note id
            user_id => requested user id
    output: single note
    '''
    query = '''SELECT * 
                FROM note_note 
                WHERE (id=%s) and (user_id=%s)''' % (id, user_id) 
    note = Note.objects.raw(query)
    return note[0]

def get_all_note(user_id):
    '''
    input : user_id => requested user id
    output: all note
    error : NoteNotFoundError
    '''
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
    '''
    input : user_id => requested user id
    output: all trash note
    error : NoteNotFoundError
    '''
    try:
        query = '''SELECT * 
                    FROM note_note 
                    WHERE (trash = true) and (user_id=%s) 
                    ORDER BY pin desc, id desc''' % user_id
        notes = Note.objects.raw(query)
        return notes
    except Exception:
        raise NotesNotFoundError(409, response_code[409])

def get_all_archive_note(user_id):
    '''
    input : user_id => requested user id
    output: all archived note
    error : NoteNotFoundError
    '''
    try:
        query = '''SELECT * 
                    FROM note_note 
                    WHERE (trash = false) and (archive = true) and (user_id=%s) 
                    ORDER BY pin desc, id desc''' % user_id
        notes = Note.objects.raw(query)
        return notes
    except Exception:
        raise NotesNotFoundError(409, response_code[409])


def get_all_label(user_id):
    '''
    input : user_id => requested user id
    output: all labels
    error : LabelNotFoundError
    '''
    try:
        query    =   '''SELECT * 
                        FROM label_label
                        WHERE user_id = %s
                        ORDER BY id desc''' % user_id
        labels = Label.objects.raw(query)
        return labels
    except Exception:
        raise LabelsNotFoundError(code=308, msg=response_code[308])

def get_single_label(id, user_id):
    '''
    input : id      => label id
            user_id => requested user id
    output: single label
    '''
    query = '''SELECT * 
                FROM label_label
                WHERE (id=%s) and (user_id=%s)''' % (id, user_id) 
    label = Label.objects.raw(query)
    return label[0]

def delete_label_and_relation(id, user_id):
    '''
    input : id      => label id
            user_id => requested user id
    output: boolean value on delete or error
    error : Exception
    '''
    try:
        label = Label.objects.get(id = id, user_id =user_id)
        mapped_notes = LabelMap.objects.filter(label_id = id)
        if mapped_notes != None:
            mapped_notes.delete()
            label.delete()
            return True
    except Exception:
        pass
    return False