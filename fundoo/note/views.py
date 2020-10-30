# View
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

# Models
from django.contrib.auth.models import User
from note.models import Note, LabelMap, UserMap
from label.models import Label

# Serializer
from note.serializers import NoteSerializer, EditNoteSerializer, GetNoteSerializer

# Response
from util.status import response_code
from util import static_data

# Decorator
from django.utils.decorators import method_decorator
from util.decorator import custom_login_required, admin_access_only
from django.views.decorators.cache import cache_page

# Exceptions
from note.exceptions import (RequestObjectDoesNotExixts, 
                            LabelMappingException,
                            NotesNotFoundError,
                            CollaboratorMappingException
                            )
from django.core.exceptions import ObjectDoesNotExist

# Repository
from services.repository import ( get_all_note,
                                  get_trashed_notes,
                                  get_archive_notes,
                                  get_single_note,
                                  delete_note,
                                  update_data,
                                  map_label,
                                  map_collaborator,
                                  create_note,
                                  get_all_users_note
                                )

# Service
from services.reminder_service import check_reminder_for_upcoming_time

# Async task
from note.task import send_reminder_mail


# import logging
import logging

# asyncio
import asyncio

from note.request_data_handler import fetch_collaborator, fetch_label, fetch_reminder, save_image


class CreateNote(GenericAPIView):
    serializer_class = NoteSerializer
    
    @method_decorator(custom_login_required)
    def post(self, request, *args, **kwargs):
        '''
        param request : Http request contains new note data and user detail
        returns : 201 created status if successful else raise validation error 
        '''
        try:
            rem_msg = None
            collab = None
            upcoming_time = False
            labels = fetch_label(request)
            collaborators = fetch_collaborator(request) #Fetch collaborators from request
            rem = fetch_reminder(request)
            if rem != None:
                upcoming_time = check_reminder_for_upcoming_time(rem)
                if not upcoming_time:
                    request.data['reminder'] = None
                    rem_msg = response_code[415]
            id = create_note(request.user.id, request.data)
            if id != -1:
                image = save_image(request)
                if labels != None:
                    map_label(id, request.user.id, labels)
                if collaborators != None:
                    collab = map_collaborator(id, collaborators)
                if upcoming_time:
                    email = request.user.email
                    send_reminder_mail.delay(rem, email)
                resp = {"code":201, 
                            "msg":response_code[201],
                            "invalid_user":collab,
                            "rem_msg":rem_msg}
                return Response(resp)
            return Response({"code":300, "msg":response_code[300]})
        except Exception as e:
            print(e)
            # logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})


class GetNote(GenericAPIView):
    serializer_class = GetNoteSerializer

    @method_decorator(custom_login_required)
    def get(self, request, *args, **kwargs):
        '''
        param request: Http request contains user detail
        returns: all notes for perticular user or raise error
        '''
        try:
            notes = get_all_note(request.user.id)
            return Response({"data":notes, "code":200, "msg":response_code[200]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})
        



class EditNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    def get_object(self,id):
        '''
        param id: Note id
        returns: single note for perticular user if user is authenticated or user in collaborators else raise RequestObjectDoesNotExixts
        '''
        try:
            note = get_single_note(id, self.request.user.id)
            return note
        except NotesNotFoundError:
           raise RequestObjectDoesNotExixts(code=409, msg=response_code[409])

    @method_decorator(custom_login_required)
    def get(self, request, id=None):
        '''
        param request, id: Http request contains user detail, id contains note id
        returns: single note or does not exist
        '''
        try:
            note       = self.get_object(id)
            return Response({"data":note,"code":200, "msg":response_code[200]})
        except RequestObjectDoesNotExixts as e:
            return Response({'code':e.code, 'msg':e.msg})
        except Exception as e:
            print(e)
            # logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})

    @method_decorator(custom_login_required)
    def put(self, request, id=None):
        '''
        param request, id: Http request new update field data, id contains note id
        returns: update note or does not exists
        '''
        rem_msg = None
        collab = None
        upcoming_time = False
        try:
            note = self.get_object(id)
            labels = fetch_label(request)
            collaborators = fetch_collaborator(request) #Fetch collaborators from request
            rem = fetch_reminder(request)
            image = save_image(request)
            if rem != None:
                upcoming_time = check_reminder_for_upcoming_time(rem)
                if not upcoming_time:
                    request.data['reminder'] = None
                    rem_msg = response_code[415]
            updated = asyncio.run(update_data(id, request.data))
            if updated:
                if labels != None:
                    map_label(id, request.user.id, labels)
                if collaborators != None:
                    collab = map_collaborator(id, collaborators)
                if upcoming_time:
                    email = request.user.email
                    send_reminder_mail.delay(rem, email)
            resp = {"data":self.get_object(id),
                    "code":200, 
                    "msg":response_code[200],
                    "invalid_user":collab, 
                    "rem_msg":rem_msg
                    }
            return Response(resp)
        except Exception as e:
            print(e)
            # logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})


class TrashNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(custom_login_required)
    def get(self, request, *args, **kwargs):
        '''
        param request: Http request contains user detail
        returns: all trash notes for perticular user or raise error
        '''
        try:
            notes = get_trashed_notes(request.user.id)
            return Response({"data":notes, "code":200, "msg":response_code[200]})
        except NotesNotFoundError as e :
            return Response({'code':e.code, 'msg':e.msg})

class ArchiveNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(custom_login_required)
    def get(self, request, *args, **kwargs):
        '''
        param request: Http request contains user detail
        returns: all archive notes for perticular user or raise error
        '''
        try:
            notes = get_archive_notes(request.user.id)
            return Response({"data":notes, "code":200, "msg":response_code[200]})
        except NotesNotFoundError as e :
            return Response({'code':e.code, 'msg':e.msg})

class DeleteNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(custom_login_required)
    def delete(self, request, id=None):
        '''
        param request, id: Http request contains user detail, id contains note id
        returns: delete perticular note or return does not exists
        '''
        try:
            delete = delete_note(id, request.user.id)
            if delete:
                return Response({"code":200, "msg":response_code[200]})
            return Response({"code":409, "msg":response_code[409]})
        except Exception as e:
            # logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})


class GetViewForAdmin(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(custom_login_required)
    @method_decorator(admin_access_only)
    def get(self, request, *args, **kwargs):
        '''
        param request: Http request contains user detail
        returns: all notes for perticular user or raise error
        '''
        try:
            notes = get_all_users_note()
            return Response({"data":notes, "code":200, "msg":response_code[200]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})
