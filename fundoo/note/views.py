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
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

# Exceptions
from note.exceptions import (RequestObjectDoesNotExixts, 
                            LabelMappingException,
                            NotesNotFoundError,
                            CollaboratorMappingException
                            )
from django.core.exceptions import ObjectDoesNotExist

# Repository
from services.repository import ( add_label_id_from_label,
                                  get_all_note,
                                  edit_label_id_from_label,
                                  get_all_trash_note,
                                  get_all_archive_note,
                                  get_single_note,
                                  add_collaborator_id_from_collaborator,
                                  delete_note_and_relation
                                )

# Service
from services.reminder_service import check_reminder_for_upcoming_time

# Async task
from note.task import send_reminder_mail

# Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




class CreateNote(GenericAPIView):
    serializer_class = NoteSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            rem_msg = None
            collab = None
            upcoming_time = False
            if not request.user.is_authenticated:
                return Response({"code":413, "msg":response_code[413]})
            try:
                labels = request.data.get('labels')
            except KeyError:
                pass
            try:
                collaborators = request.data.get('collaborators')
            except KeyError:
                pass
            try:
                rem = request.data.get('reminder')
                upcoming_time = check_reminder_for_upcoming_time(rem)
                if not upcoming_time:
                    request.data['reminder'] = None
                    rem_msg = response_code[415]
            except KeyError:
                pass
            serializer = NoteSerializer(data = request.data)
            if serializer.is_valid():
                instance = serializer.save(user = request.user)
                if labels != None:
                    try:
                        add_label_id_from_label(labels, instance, request.user)
                    except LabelMappingException as e:
                        return Response({"code":e.code, "msg":e.msg})
                if collaborators != None:
                    try:
                        collab = add_collaborator_id_from_collaborator(collaborators, instance, request.user)
                    except CollaboratorMappingException as e:
                        return Response({"code":e.code, "msg":e.msg})
                resp = {"code":201, 
                        "msg":response_code[201],
                        "invalid_user":collab,
                        "rem_msg":rem_msg}
                if upcoming_time:
                    email = request.user.email
                    send_reminder_mail.delay(rem, email)
                return Response(resp)
            return Response({"code":300, "msg":response_code[300]})
        except Exception as e:
            print(e)
            return Response({"code":416, "msg":response_code[416]})


class GetNote(GenericAPIView):
    serializer_class = GetNoteSerializer

    @method_decorator(login_required)
    @method_decorator(cache_page(60*10))
    def get(self, request, *args, **kwargs):
        try:
            notes = get_all_note(request.user.id)
            
            paginator = Paginator(notes, static_data.ITEMS_PER_PAGE)
            page_number = request.GET.get('page', 1)
            try:
                notes = paginator.page(page_number)
            except PageNotAnInteger:
                notes = paginator.page(1)
            except EmptyPage:
                notes = paginator.page(paginator.num_pages)
            serializer = GetNoteSerializer(notes, many=True)
            return Response({"data":serializer.data, "code":200, "msg":response_code[200]})
        except NotesNotFoundError as e:
            return Response({"code":e.code, "msg":e.msg})



class EditNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    def get_object(self,id):
        try:
            note = get_single_note(id, self.request.user.id)
            return note
        except NotesNotFoundError:
           raise RequestObjectDoesNotExixts(code=409, msg=response_code[409])

    @method_decorator(login_required)
    def get(self, request, id=None):
        try:
            try:
                note       = self.get_object(id)
            except RequestObjectDoesNotExixts as e:
                return Response({'code':e.code, 'msg':e.msg})
            serializer = EditNoteSerializer(note)
            return Response({"data":serializer.data,"code":200, "msg":response_code[200]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})

    @method_decorator(login_required)
    def put(self, request, id=None):
        rem_msg = None
        collab = None
        upcoming_time = False
        try:
            try:
                note       = self.get_object(id)
            except RequestObjectDoesNotExixts as e:
                return Response({'code':e.code, 'msg':e.msg})
            try:
                labels = request.data.get('labels')
            except KeyError:
                pass
            try:
                collaborators = request.data.get('collaborators')
            except KeyError:
                pass
            try:
                rem = request.data.get('reminder')
                upcoming_time = check_reminder_for_upcoming_time(rem)
                if not upcoming_time:
                    request.data['reminder'] = None
                    rem_msg = response_code[415]
            except KeyError:
                pass
            serializer = EditNoteSerializer(note, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save(user = request.user)
                if labels != None:
                    delete_existing_relation = LabelMap.objects.filter(note = instance).delete()
                    edit_label_id_from_label(labels, instance, request.user)
                if collaborators != None:
                    delete_existing_user_relation = UserMap.objects.filter(note = instance).delete()
                    try:
                        collab = add_collaborator_id_from_collaborator(collaborators, instance, request.user)
                    except CollaboratorMappingException as e:
                        return Response({"code":e.code, "msg":e.msg})
                if upcoming_time:
                    email = request.user.email
                    send_reminder_mail.delay(rem, email)
                resp = {
                        "data":serializer.data,
                        "code":200, 
                        "msg":response_code[200],
                        "invalid_user":collab, 
                        "rem_msg":rem_msg
                        }
                return Response(resp)
            return Response({"code":300, "msg":response_code[300]})
        except Exception as e:
            return Response({"code":416, "msg":response_code[416]})

class TrashNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            notes = get_all_trash_note(request.user.id)
            serializer = EditNoteSerializer(notes, many=True)
            return Response({"data":serializer.data, "code":200, "msg":response_code[200]})
        except NotesNotFoundError as e :
            return Response({'code':e.code, 'msg':e.msg})

class ArchiveNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            notes = get_all_archive_note(request.user.id)
            serializer = EditNoteSerializer(notes, many=True)
            return Response({"data":serializer.data, "code":200, "msg":response_code[200]})
        except NotesNotFoundError as e :
            return Response({'code':e.code, 'msg':e.msg})

class DeleteNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(login_required)
    def delete(self, request, id=None):
        try:
            delete_note = delete_note_and_relation(id, request.user.id)
            if delete_note:
                return Response({"code":200, "msg":response_code[200]})
            return Response({"code":409, "msg":response_code[409]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})


