from rest_framework import serializers

from friends.models import Friend
from users.serializers import UserSerializer


class FriendsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    friend = UserSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ('user', 'friend', 'date_added')


class FriendOnlyFriendsSerializer(serializers.ModelSerializer):
    friend = UserSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ('friend', 'date_added')