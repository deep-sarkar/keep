from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from note.models import Note, LabelMap
from label.models import Label
from note.serializers import NoteSerializer, EditNoteSerializer, GetNoteSerializer
from util.status import response_code
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from note.exceptions import RequestObjectDoesNotExixts
from django.core.exceptions import ObjectDoesNotExist

class CreateNote(GenericAPIView):
    serializer_class = NoteSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return Response({"code":413, "msg":response_code[413]})
            try:
                labels = request.data.get('labels')
            except KeyError:
                pass
            serializer = NoteSerializer(data = request.data)
            if serializer.is_valid():
                instance = serializer.save(user = request.user)
                if labels != None:
                    for label in labels:
                        try:
                            single_label = Label.objects.get(name = label, user = request.user.id)
                        except ObjectDoesNotExist:
                            single_label = Label.objects.create(name = label, user = request.user)
                        try:
                            LabelMap.objects.create(label=single_label, note = instance)
                        except Exception as e:
                            return Response({"code":417, "msg":response_code[417]})
                    return Response({"code":201, "msg":response_code[201]})
            return Response({"code":300, "msg":response_code[300]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})


class GetNote(GenericAPIView):
    serializer_class = GetNoteSerializer

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            query = '''SELECT * 
                       FROM note_note 
                       WHERE (trash = false) and (archive = false) and (user_id=%s) 
                       ORDER BY pin desc, id desc''' % user_id
            notes = Note.objects.raw(query)
            serializer = GetNoteSerializer(notes, many=True)
            return Response({"data":serializer.data, "code":200, "msg":response_code[200]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})



class EditNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    def get_object(self,id):
        try:
            user_id = self.request.user.id
            query = '''SELECT * 
                        FROM note_note 
                        WHERE (id=%s) and (user_id=%s)''' % (id, user_id) 
            note = Note.objects.raw(query)
            return note[0]
        except IndexError:
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
        try:
            try:
                note       = self.get_object(id)
            except RequestObjectDoesNotExixts as e:
                return Response({'code':e.code, 'msg':e.msg})
            try:
                labels = request.data.get('labels')
            except KeyError:
                pass
            serializer = EditNoteSerializer(note, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save(user = request.user)
                if labels != None:
                    delete_existing_relation = LabelMap.objects.filter(note = instance).delete()
                    for label in labels:
                        try:
                            single_label = Label.objects.get(name = label, user = request.user.id)
                        except ObjectDoesNotExist:
                            single_label = Label.objects.create(name = label, user = request.user)
                        try:
                            LabelMap.objects.get(label=single_label, note = instance)
                        except ObjectDoesNotExist:
                            LabelMap.objects.create(label=single_label, note = instance)
                return Response({"data":serializer.data,"code":200, "msg":response_code[200]})
            return Response({"code":300, "msg":response_code[300]})
        except Exception as e:
            return Response({"code":416, "msg":response_code[416]})

class TrashNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        query = '''SELECT *
                   FROM note_note
                   WHERE (trash = true) and (user_id = %s) 
                   ORDER BY id desc''' %user_id
        notes = Note.objects.raw(query)
        serializer = EditNoteSerializer(notes, many=True)
        return Response({"data":serializer.data, "code":200, "msg":response_code[200]})

class ArchiveNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        query = '''SELECT *
                   FROM note_note
                   WHERE (archive = true) and (trash = false) and (user_id = %s) 
                   ORDER BY id desc''' %user_id
        notes = Note.objects.raw(query)
        serializer = EditNoteSerializer(notes, many=True)
        return Response({"data":serializer.data, "code":200, "msg":response_code[200]})



