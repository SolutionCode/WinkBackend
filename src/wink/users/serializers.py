from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework import generics
from rest_framework.serializers import ValidationError
# from permissions import IsAuthenticatedOrCreate

from users.models import User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'url',
            'email',
            'display_name',
            'username'
        )
