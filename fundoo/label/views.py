from django.shortcuts import render
from label.models import Label
from util.status import response_code
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from note.exceptions import RequestObjectDoesNotExixts
from django.core.exceptions import ObjectDoesNotExist
from label.serializers import LabelSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from note.models import LabelMap

class CreateLabel(GenericAPIView):
    serializer_class = LabelSerializer

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        user = request.user
        try:
            label = Label.objects.get(name = name, user = user)
            return Response({"code":307, "msg":response_code[307]})
        except ObjectDoesNotExist:
            label = Label.objects.create(name = name, user = user)
            return Response({"code":201, "msg":response_code[201]})
        return Response({"code":300, "msg":response_code[300]})


class GetLabel(GenericAPIView):
    serializer_class = LabelSerializer

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id  = request.user.id
        query    = '''SELECT * 
                      FROM label_label
                      WHERE user_id = %s
                      ORDER BY id desc''' % user_id
        labels = Label.objects.raw(query)
        serializer = LabelSerializer(labels, many = True)
        return Response({"data":serializer.data,"code":200, "msg":response_code[200]})

class EditLabel(GenericAPIView):
    serializer_class = LabelSerializer

    def get_object(self, id=None):
        try:
            user_id = self.request.user.id
            query = '''SELECT * 
                        FROM label_label
                        WHERE (id=%s) and (user_id=%s)''' % (id, user_id) 
            label = Label.objects.raw(query)
            return label[0]
        except IndexError:
           raise RequestObjectDoesNotExixts(code=409, msg=response_code[409])

    @method_decorator(login_required)
    def get(self, request, id=None):
        try:
            try:
                label = self.get_object(id)
            except RequestObjectDoesNotExixts as e:
                return Response({'code':e.code, 'msg':e.msg})
            serializer = LabelSerializer(label)
            return Response({"data":serializer.data,"code":200, "msg":response_code[200]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})

    @method_decorator(login_required)
    def put(self, request, id=None):
        try:
            label = self.get_object(id)
        except RequestObjectDoesNotExixts as e:
            return Response({'code':e.code, 'msg':e.msg})
        serializer = LabelSerializer(label, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response({"data":serializer.data,"code":200, "msg":response_code[200]})
        return Response({"code":300, "msg":response_code[300]})

class DeleteLabel(GenericAPIView):
    serializer_class = LabelSerializer

    @method_decorator(login_required)
    def delete(self, request, id=None):
        try:
            user_id = request.user.id
            try:
                label = Label.objects.get(id = id, user_id =user_id)
                mapped_notes = LabelMap.objects.filter(label_id = id)
                if mapped_notes != None:
                    mapped_notes.delete()
                    label.delete()
                return Response({"code":200, "msg":response_code[200]})
            except ObjectDoesNotExist:
                return Response({"code":308, "msg":response_code[308]})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})