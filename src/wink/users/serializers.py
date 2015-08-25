from rest_framework.serializers import HyperlinkedModelSerializer

from users.models import User


class UserSerializer(HyperlinkedModelSerializer):
    resource_name = 'user'

    class Meta:
        model = User
        fields = (
            'id',
            'url',
            'email',
            'display_name',
            'username'
        )


class UserPublicSerializer(HyperlinkedModelSerializer):
    resource_name = 'user_public'

    class Meta:
        model = User
        fields = (
            'id',
            'url',
            'display_name',
            'username'
        )