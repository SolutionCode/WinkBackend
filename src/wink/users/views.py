from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from common.permissions import is_owner
from common.renderers import JSONRenderer
from users.models import User
from users.serializers import UserSerializer, UserPublicSerializer


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'options']
    renderer_classes = (JSONRenderer,)

    permission_classes = (IsAuthenticated, is_owner())


class UserPublicRetrieveUpdateView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    http_method_names = ['get', 'options']
    renderer_classes = (JSONRenderer,)

    permission_classes = (IsAuthenticated,)


class UserPublicListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    renderer_classes = (JSONRenderer,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('username',)
    search_fields = ('display_name', 'username')

    permission_classes = (IsAuthenticated,)
