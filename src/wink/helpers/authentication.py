from rest_framework.response import Response

from helpers.errors import Error, ErrorType

def check_authorization(self, request):
    if request.user.is_anonymous():
        error = Error(ErrorType.unauthorized)
        return Response(data=error.__dict__,status=401)
    else:
        return None