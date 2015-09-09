from oauth2_provider.models import Application

__author__ = 'sacherus'

from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist


class SocialTokenSerializer(serializers.Serializer):
    ALLOWED_BACKENDS = ['facebook']

    backend = serializers.CharField(max_length=200)
    social_token = serializers.CharField(max_length=255)
    # client_id = serializers.CharField(max_length=200)
    # client_secret = serializers.CharField(max_length=200)
    # save some queries to DB
    # app = None

    def validate_backend(self, value):
        """
        Check that backend is facebook (in fut. google eg.)
        """
        if value not in self.ALLOWED_BACKENDS:
            raise serializers.ValidationError("Allowed backends: " + str(self.ALLOWED_BACKENDS))
        return value

    # def validate_client_id(self, value):
    #     """
    #     Check client id exists in database
    #     """
    #     try:
    #         self.app = Application.objects.get(client_id=value)
    #     except ObjectDoesNotExist:
    #         raise serializers.ValidationError("Application with id " + value + " doest not exist in DB")
    #     return value
