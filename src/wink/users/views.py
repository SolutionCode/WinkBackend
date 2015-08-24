from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsOwner
from users.models import User
from users.serializers import UserSerializer


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'options']

    permission_classes = (IsAuthenticated, IsOwner())
