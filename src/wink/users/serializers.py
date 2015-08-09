from rest_framework.serializers import HyperlinkedModelSerializer

from users.models import User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'email', 'display_name', 'username')

from rest_framework import serializers


class SignUpSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'password', 'client_id', 'client_secret')
        write_only_fields = ('password',)

    def get_client_id(self, obj):
        return obj.application_set.first().client_id

    def get_client_secret(self, obj):
        return obj.application_set.first().client_secret


from rest_framework import generics
from permissions import IsAuthenticatedOrCreate

class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate,)