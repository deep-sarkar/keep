from rest_framework import serializers
from note.models import Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ['id', 'user', 'trash']

class EditNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ['id', 'user']

    def update(self, instance, validated_data):
        instance.title     = validated_data.get("title", instance.title)
        instance.note      = validated_data.get("note", instance.note)
        instance.image     = validated_data.get("image", instance.image)
        instance.reminder  = validated_data.get("reminder", instance.reminder)
        instance.archive   = validated_data.get("archive", instance.archive)
        instance.trash     = validated_data.get("trash", instance.trash)
        instance.pin       = validated_data.get("pin", instance.pin)
        instance.save()
        return instance