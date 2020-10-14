from django.shortcuts import render
from label.models import Label
from util.status import response_code
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from note.exceptions import RequestObjectDoesNotExixts, LabelsNotFoundError
from django.core.exceptions import ObjectDoesNotExist
from label.serializers import LabelSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from note.models import LabelMap
from services.repository import get_all_label, delete_label_and_relation, get_single_label

class CreateLabel(GenericAPIView):
    serializer_class = LabelSerializer

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        '''
        param request: Http request contains user detail, new label data
        returns: 201 created or validation error
        '''
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
        '''
        param request: Http request contains user detail
        returns: all labels or Labels not found
        '''
        try:
            labels = get_all_label(request.user.id)
            serializer = LabelSerializer(labels, many = True)
            return Response({"data":serializer.data,"code":200, "msg":response_code[200]})
        except LabelsNotFoundError as e:
            return Response({'code':e.code, 'msg':e.msg})


class EditLabel(GenericAPIView):
    serializer_class = LabelSerializer

    def get_object(self, id=None):
        '''
        param id: Label id
        returns: single label or raise error
        '''
        try:
           label = get_single_label(id, self.request.user.id)
           return label
        except IndexError:
           raise RequestObjectDoesNotExixts(code=409, msg=response_code[409])

    @method_decorator(login_required)
    def get(self, request, id=None):
        '''
        param request, id: Http request contains user detail, id contains label id
        returns: single label or does not exist
        '''
        
        try:
            label = self.get_object(id)
            serializer = LabelSerializer(label)
            return Response({"data":serializer.data,"code":200, "msg":response_code[200]})
        except RequestObjectDoesNotExixts as e:
            return Response({'code':e.code, 'msg':e.msg})
        except Exception:
            return Response({"code":416, "msg":response_code[416]})

    @method_decorator(login_required)
    def put(self, request, id=None):
        '''
        param request, id: Http request new update field data, id contains label id
        returns: update label or does not exists
        '''
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
        '''
        param request, id: Http request contains user detail, id contains label id
        returns: delete perticular label and relation with notes or return does not exists
        '''
        try:
            delete_label = delete_label_and_relation(id, request.user.id)
            if delete_label:
                return Response({"code":200, "msg":response_code[200]})
            return Response({"code":416, "msg":response_code[416]})
        except ObjectDoesNotExist:
            return Response({"code":308, "msg":response_code[308]})
