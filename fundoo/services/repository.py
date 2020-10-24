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
from asgiref.sync import sync_to_async


'''
                                                                CONVERTER
'''


def fetchalldict(cursor):
    '''
    param: cursor object
    return: dictionary of query
    '''
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def tuple_to_list(tuple_of_tuple):
    '''
    param: tuple of tuple containing string value
    return: list of string value
    '''
    collaborators = [user[0] for user in tuple_of_tuple]
    return collaborators


def get_collaborators(note_id):
    '''
    param: note_id
    return: list of username
    '''
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT username 
                            FROM auth_user
                            INNER JOIN note_usermap
                            ON auth_user.id = note_usermap.user_id
                            INNER JOIN note_note
                            ON note_note.id = note_usermap.note_id
                            WHERE note_note.id = %s""",[note_id])
        data = cursor.fetchall()
        collab = tuple_to_list(data)
        return collab
    except Exception:
        return []
    finally:
        cursor.close()



def get_labels(note_id):
    '''
    param: note_id
    return: list of lable (string value)
    '''
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT name
                            FROM label_label
                            INNER JOIN note_labelmap
                            ON label_label.id = note_labelmap.label_id
                            INNER JOIN note_note
                            ON note_note.id = note_labelmap.note_id
                            WHERE note_note.id = %s""",[note_id])
        data = cursor.fetchall()
        labels = tuple_to_list(data)
        return labels
    except Exception:
        return []
    finally:
        cursor.close()



# GET SINGLE NOTE

def get_single_note(note_id, user_id):
    try:
        cursor = connection.cursor()
        cursor.execute("Select * from note_note where id = %s and user_id = %s",[note_id,user_id])
        data = fetchalldict(cursor)
        data[0]['labels'] = get_labels(note_id)   #get all labels for perticular note
        data[0]['collaborators'] = get_collaborators(note_id) #get all collaborators for single note
        return data[0]
    except Exception as e:
        raise NotesNotFoundError(code=409, msg=response_code[409])
    finally:
        cursor.close()


# Update new data in existing note by field and field value

@sync_to_async
def update_note(note_id, attribute, value):
    '''
    param: note_id, attributr (column name), value (row value)
    return: True if updated
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'''UPDATE note_note
                                    SET {attribute} = %s
                                    WHERE id = %s''',[value, note_id])
            data = cursor.fetchall()
            return True
    except Exception as e:
        return False


# Pass table column name and column data into update note function
async def update_data(note_id, new_data):
    '''
    param: note_id, new_data (new data to update note)
    return: True after update or false if exception occoured
    '''
    try:
        for key in new_data:
            value = new_data[key]
            await asyncio.gather(update_note(note_id, key, value))
        return True
    except Exception as e:
        return False






# LABELS

def get_label_id(label_name, user_id):
    '''
    params: label_name, user_id
    return: label id if exists or -1
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_label',[label_name,user_id])
            data = cursor.fetchall()
            return data[0][0]
    except Exception:
        return -1

def create_label_and_get_id(label_name, user_id):
    '''
    param: label_name, user_id
    return: label id after creating label
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_insert_label',[label_name, user_id])
            data = cursor.fetchall()
            data = data[0][0]
            return data
    except Exception as e:
        return None

def delete_old_label_relation(note_id):
    '''
    param: note_id
    return: True after deleting all old relation for label with note
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute('''DELETE FROM note_labelmap
                                WHERE note_id = %s''',[note_id])
            data = cursor.fetchall()
            return True
    except Exception:
        return False

def create_label_relation(note_id, label_id):
    '''
    params: note_id, label_id
    function: create a new relation for perticular label with note
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute('''INSERT INTO note_labelmap(note_id, label_id)
                                VALUES(%s, %s)''',[note_id, label_id])
            cursor.fetchall()
    except Exception as e:
        pass

def map_label(note_id, user_id, labels):
    '''
    param: note_id, user_id, labels (list of label)
    function: map all labels for perticular note
    '''
    try:
        delete_old_label_relation(note_id)
        for label in labels:
            label_id = get_label_id(label, user_id)
            if label_id == -1:
                label_id = create_label_and_get_id(label, user_id)
            create_label_relation(note_id, label_id)
    except Exception as e:
        pass





# COLLABORATORS

def get_user_id(username):
    '''
    params: username
    return: user id if exists or -1
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_get_user',[username])
            user_id = cursor.fetchall()
            user_id = user_id[0][0]
            return user_id
    except Exception:
        return -1

def delete_old_collaborator_relations(note_id):
    '''
    params: note_id
    function: delete all collaborator relation for perticular note
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM note_usermap
                                WHERE note_id = %s""",[note_id])
            cursor.fetchall()
            return True
    except Exception:
        return False

def create_collaborator_relation(note_id, user_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute('''INSERT INTO note_usermap(note_id, user_id)
                                VALUES(%s, %s)''',[note_id, user_id])
            cursor.fetchall()
    except Exception:
        pass

def map_collaborator(note_id, collaborators):
    '''
    param: note_id, collaborators (list of user)
    '''
    invalid_user = []
    try:
        delete_old_collaborator_relations(note_id)
        for username in collaborators:
            user_id = get_user_id(username)
            if user_id == -1:
                invalid_user.append(username)
            else:
                create_collaborator_relation(note_id, user_id)
    except Exception:
        pass
    


# CREATE NOTE
def insert_note_into_note_table(note):
    '''
    param: note data (dictionary)
    return: note id if created else -1
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_create_note_and_get_id',[note['title'],note['note'],note['image'],
                                                note['reminder'],note['archive'],note['trash'],note['pin'],
                                                note['color'],note['user_id'],])
            id = cursor.fetchall()
            return id[0][0]
    except Exception as e:
        return -1


def create_note(user_id, note_data):
    '''
    param: user_id, note_data
    return: note id if created else -1
    '''
    note = {
        'title':None,
        'note':None,
        'image':None,
        'reminder':None,
        'archive':False,
        'trash':False,
        'pin':False,
        'color':'#ffffff',
        'user_id':user_id
    }
    try:
        for key in note_data:
            note[key] = note_data[key]
        id = insert_note_into_note_table(note)
        return id
    except Exception as e:
        return -1


@sync_to_async
def string_to_list(string_value):
    '''
    param: string form of labels and collaborator
    return: list of labels and collaborators or None
    '''
    try:
        if len(string_value) != 0:
            list_of_str = string_value.split(',')
            list_of_str.pop()
            return list_of_str
        return None
    except Exception as e:
        return None

async def get_label_and_collab_list(notes):
    for note in notes:
        note['collaborators'] = await string_to_list(note['collaborators'])
        note['labels'] = await string_to_list(note['labels'])
    return notes

# GET all note
def get_all_note(user_id):
    '''
    param : user_id
    return: all notes except trash and archive
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_get_all_note',[user_id])
            data = fetchalldict(cursor)
        colab_notes = get_collaborated_notes(user_id)
        if len(colab_notes) != 0:
            if len(data) == 0:
                data = colab_notes
            else:
                data.append(colab_notes)
        notes = asyncio.run(get_label_and_collab_list(data))
        return notes
    except Exception as e:
        return []


def get_trashed_notes(user_id):
    '''
    param: user_id
    return: all trash note for perticular user
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_get_trash_note',[user_id])
            data = fetchalldict(cursor)
            return data
    except Exception:
        return []


def get_archive_notes(user_id):
    '''
    param: user_id
    return: all archive note for perticular user
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_get_archive_note',[user_id])
            data = fetchalldict(cursor)
            return data
    except Exception:
        return []


def get_collaborated_notes(user_id):
    '''
    param: user_id
    return: all collaborated note for perticular user
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_get_collaborated_note', [user_id])
            data = fetchalldict(cursor)
            return data
    except Exception:
        return []


def check_trash_exists(note_id, user_id):
    '''
    param: note_id, user_id
    return: 1 if trash exists else 0
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_to_check_trash_exists',[note_id, user_id])
            data = cursor.fetchall()
            return data[0][0]
    except Exception:
        return 0

def delete_note(note_id, user_id):
    '''
    param: note_id, user_id
    return: True if trash Deleted else False
    '''
    try:
        trash_exist = check_trash_exists(note_id, user_id)
        if trash_exist == 1:
            delete_old_label_relation(note_id)
            delete_old_collaborator_relations(note_id)
            with connection.cursor() as cursor:
                cursor.execute('''DELETE FROM note_note where id = %s''',[note_id])
                cursor.fetchall()
        return True
    except Exception:
        return False



def get_all_users_note():
    '''
    return: all notes existed in db
    '''
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_get_all_users_note')
            data = fetchalldict(cursor)
            return data
    except Exception:
        return []


def get_all_label(user_id):
    '''
    input : user_id => requested user id
    output: all labels
    error : LabelNotFoundError
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT *
                              FROM label_label
                              WHERE user_id = %s''',[user_id])
            labels = fetchalldict(cursor)
            return labels
    except Exception:
        raise LabelsNotFoundError(code=308, msg=response_code[308])

def get_single_label(id, user_id):
    '''
    input : id      => label id
            user_id => requested user id
    output: single label
    '''
    try:
        with connection.cursor() as cursor:
            query = '''SELECT * 
                        FROM label_label
                        WHERE (id=%s) and (user_id=%s)''' % (id, user_id) 
            cursor.execute(query)
            label = fetchalldict(cursor)
            return label
    except Exception:
        return []

def edit_label(label, label_id, user_id):
    '''
    param: label, label_id, user_id
    return: true id updated else false
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute('''UPDATE label_label 
                                SET name = %s
                                WHERE id = %s and user_id = %s''',[label, label_id, user_id])
        return True
    except Exception as e:
        return False

def delete_label_note_relation(label_id):
    '''
    param: label_id
    return: True after deleting all old relation for label with note
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute('''DELETE FROM note_labelmap
                                WHERE label_id = %s''',[label_id])
            data = cursor.fetchall()
            return True
    except Exception:
        return False


def delete_label_and_relation(label_id, user_id):
    '''
    input : id      => label id
            user_id => requested user id
    output: boolean value on delete or error
    error : Exception
    '''
    try:
        label = get_single_label(label_id, user_id)
        if len(label) != 0:
            del_mapped_relation = delete_label_note_relation(label_id)
            if del_mapped_relation:
                with connection.cursor() as cursor:
                    cursor.execute('''DELETE 
                                      FROM label_label
                                      WHERE id = %s''',[label_id])
                    cursor.fetchall()
                return True
        return False
    except Exception as e:
        return False
