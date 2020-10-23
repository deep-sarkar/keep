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
from services.repository import get_all_label, delete_label_and_relation, get_single_label, edit_label
import logging

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
            return Response({"data":labels,"code":200, "msg":response_code[200]})
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
            return Response({"data":label,"code":200, "msg":response_code[200]})
        except RequestObjectDoesNotExixts as e:
            return Response({'code':e.code, 'msg':e.msg})
        except Exception as e:
            logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})

    @method_decorator(login_required)
    def put(self, request, id=None):
        '''
        param request, id: Http request new update field data, id contains label id
        returns: update label or does not exists
        '''
        try:
            label = request.data.get('name')
            update = edit_label(label, id, request.user.id)
            if update:
                updated_label = self.get_object(id)
            return Response({"data":updated_label,"code":200, "msg":response_code[200]})
        except RequestObjectDoesNotExixts as e:
            return Response({'code':e.code, 'msg':e.msg})
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
