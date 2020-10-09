from note.models import LabelMap
from label.models import Label
from django.core.exceptions import ObjectDoesNotExist
from note.exceptions import LabelMappingException
from util.status import response_code

def add_label_id_from_label(labels, instance, user):
    for label in labels:
        try:
            single_label = Label.objects.get(name = label, user = user.id)
        except ObjectDoesNotExist:
            single_label = Label.objects.create(name = label, user = user)
        try:
            LabelMap.objects.create(label=single_label, note = instance)
        except Exception:
            raise LabelMappingException(code=417, msg=response_code[417])