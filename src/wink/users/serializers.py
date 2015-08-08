from rest_framework.serializers import  ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'display_name', 'handle')
