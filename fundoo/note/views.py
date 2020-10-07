from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from note.models import Note
from note.serializers import NoteSerializer, EditNoteSerializer
from status import response_code
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from note.exceptions import ObjectDoesNotExixts
from django.db import connections

class CreateNote(GenericAPIView):
    serializer_class = NoteSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return Response({"code":413, "msg":response_code[413]})
            serializer = NoteSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(user = request.user)
                return Response({"code":201, "msg":response_code[201]})
            return Response({"code":300, "msg":response_code[300]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})


class GetNote(GenericAPIView):
    serializer_class = NoteSerializer

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            query = 'SELECT * FROM note_note WHERE (trash = false) and (archive = false) and (user_id=%s) ' % user_id
            notes = Note.objects.raw(query)
            serializer = NoteSerializer(notes, many=True)
            return Response({"data":serializer.data, "code":200, "msg":response_code[200]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})



class EditNote(GenericAPIView):
    serializer_class = EditNoteSerializer

    def get_object(self,id):
        try:
            user_id = self.request.user.id
            # note = Note.objects.filter(Q(user=user) & Q(trash=False))
            query = "SELECT * FROM note_note WHERE id=%s" % id
            note = Note.objects.raw(query)
            return note[0]
        except IndexError:
           raise ObjectDoesNotExixts(code=409, msg=response_code[409])

    def get(self, request, id=None):
        try:
            try:
                note       = self.get_object(id)
            except ObjectDoesNotExixts as e:
                return Response({'code':e.code, 'msg':e.msg})
            serializer = EditNoteSerializer(note)
            return Response({"data":serializer.data,"code":200, "msg":response_code[200]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})