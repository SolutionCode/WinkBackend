from rest_framework import serializers
from .models import Friend
from users.serializers import UserSerializer


class FriendsSerializer(serializers.ModelSerializer):
    user_id = UserSerializer( read_only=True)
    friend_id = UserSerializer( read_only=True)
    class Meta:
        model = Friend
        fields=('user_id', 'friend_id', 'date_added')

class FriendOnlyFriendsSerializer(serializers.ModelSerializer):
    friend_id = UserSerializer( read_only=True)
    class Meta:
        model = Friend
        fields=('friend_id', 'date_added')
