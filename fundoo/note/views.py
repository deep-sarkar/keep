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




