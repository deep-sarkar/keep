from rest_framework import serializers
from label.models import Label

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Label
        fields = '__all__'