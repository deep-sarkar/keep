from rest_framework import serializers
from note.models import Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model            = Note
        fields           = "__all__"
        read_only_fields = ['id', 'user', 'trash']

class GetNoteSerializer(serializers.ModelSerializer):
    labels        = serializers.StringRelatedField(many=True)
    collaborators = serializers.StringRelatedField(many=True)
    class Meta:
        model            = Note
        fields           = "__all__"
        read_only_fields = ['id', 'user', 'trash']

class EditNoteSerializer(serializers.ModelSerializer):
    labels = serializers.StringRelatedField(many=True, read_only = True)
    collaborators = serializers.StringRelatedField(many=True, read_only = True)
    class Meta:
        model            = Note
        fields           = "__all__"
        read_only_fields = ['id', 'user']

  