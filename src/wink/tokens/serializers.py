__author__ = 'sacherus'


from rest_framework import serializers

class SocialTokenSerializer(serializers.Serializer):
    backend = serializers.CharField(max_length=200)
    social_token = serializers.CharField(max_length=200)