from django.conf import settings

__author__ = 'sacherus'

from rest_framework import serializers


class SocialTokenSerializer(serializers.Serializer):
    '''
    only as input
    '''
    backend = serializers.ChoiceField(choices=settings.ALLOWED_BACKENDS, default='facebook')
    social_token = serializers.CharField(max_length=255)


class OAuthTokenSerializer(serializers.Serializer):
    '''
    only as output
    '''
    resource_name = 'token'
    access_token = serializers.CharField(max_length=255)
    expires_in = serializers.CharField(max_length=255)
    token_type = serializers.ChoiceField(choices=['Bearer'], default='Bearer')
    refresh_token = serializers.CharField(max_length=255)
    scope = serializers.CharField(max_length=255)


class EmptySerializer(serializers.Serializer):
    # TODO: this is... Hacking!
    resource_name = ''
