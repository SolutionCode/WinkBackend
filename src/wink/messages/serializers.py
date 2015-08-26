from rest_framework import serializers

from messages.models import Message
from users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('from_user', 'to_user', 'body', 'created_at')

class BodyDateOnlyMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('body', 'created_at')
