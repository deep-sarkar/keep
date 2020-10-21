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
from django.db.models import Q
from django.db import connection
import asyncio

def fetchalldict(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def tuple_to_list(user_tuple):
    collaborators = [user[0] for user in user_tuple]
    return collaborators

def get_collaborators(id):
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT username 
                            FROM auth_user
                            INNER JOIN note_usermap
                            ON auth_user.id = note_usermap.user_id
                            INNER JOIN note_note
                            ON note_note.id = note_usermap.note_id
                            WHERE note_note.id = %s""",[id])
        data = cursor.fetchall()
        collab = tuple_to_list(data)
        return collab
    except Exception:
        return []
    finally:
        cursor.close()

def get_labels(id):
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT name
                            FROM label_label
                            INNER JOIN note_labelmap
                            ON label_label.id = note_labelmap.label_id
                            INNER JOIN note_note
                            ON note_note.id = note_labelmap.note_id
                            WHERE note_note.id = %s""",[id])
        data = cursor.fetchall()
        labels = tuple_to_list(data)
        return labels
    except Exception:
        return []
    finally:
        cursor.close()

def get_single_note(id, user_id):
    try:
        cursor = connection.cursor()
        cursor.execute("Select * from note_note where id = %s and user_id = %s",[id,user_id])
        data = fetchalldict(cursor)
        data[0]['labels'] = get_labels(id)
        data[0]['collaborators'] = get_collaborators(id)
        return data[0]
    except Exception as e:
        raise NotesNotFoundError(code=409, msg=response_code[409])
    finally:
        cursor.close()

def update_note(id, attribute, value):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'''UPDATE note_note
                                SET {attribute} = %s
                                WHERE id = %s''',[value, id])
            data = cursor.fetchall()
    except Exception as e:
        pass

def update_data(id, new_data):
    try:
        for key in new_data:
            value = new_data[key]
            update_note(id, key, value)
        return True
    except Exception as e:
        print("exc",e)
        return False

def get_label_id(label_name, user_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_label',[label_name,user_id])
            data = cursor.fetchall()
            return data[0][0]
    except Exception:
        return None

def create_label_and_get_id(label_name, user_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_insert_label',[label_name, user_id])
            data = cursor.fetchall()
            data = data[0][0]
    except Exception as e:
        print(e)
        return None

    





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

# def get_single_note(id, user_id):
#     '''
#     input : id      => requested note id
#             user_id => requested user id
#     output: single note
#     '''
#     try:
#         try:
#             note = Note.objects.get(id=id, user_id=user_id)
#         except ObjectDoesNotExist:
#             note = Note.objects.get(id=id, collaborators__in=[user_id])
#         return note
#     except Exception:
#         raise NotesNotFoundError(code=409, msg=response_code[409])


def get_all_note(user_id):
    '''
    input : user_id => requested user id
    output: all note
    error : NoteNotFoundError
    '''
    try:
        notes = Note.objects.filter(Q(trash=False) and Q(arhive=False) and Q(user_id=user_id))
        try:
            collabs_note = Note.objects.filter(Q(trash=False) and Q(arhive=False) 
                                            and Q(collaborators__in=[user_id]))
        except Exception as e:
            pass
        if collabs_note.exists():
            notes = notes.union(collabs_note)
        return notes.order_by('-id')
    except Exception:
        raise NotesNotFoundError(code=409, msg=response_code[409])

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
        print(labels)
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
    print("label",label)
    print("label 0",label[0])
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

def delete_note_and_relation(id, user_id):
    try:
        note = Note.objects.get(id = id, trash = True, user_id = user_id)
        mapped_notes     = LabelMap.objects.filter(note_id = id)
        mapped_user_note = UserMap.objects.filter(note_id = id) 
        print(mapped_notes)
        if mapped_notes != None:
            mapped_notes.delete()
            mapped_user_note.delete()
            note.delete()
            return True
    except Exception:
        return False
    return False
