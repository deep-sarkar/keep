from django.shortcuts import render
from label.models import Label
from status import response_code
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from note.exceptions import RequestObjectDoesNotExixts
from django.core.exceptions import ObjectDoesNotExist
from label.serializers import LabelSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

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


