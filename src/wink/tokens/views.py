import json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from oauth2_provider.views import TokenView


class WinkTokenView(TokenView):
    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        '''
        extended OAuth token view, because error should be changed to errors
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        url, headers, body, status = self.create_token_response(request)
        d = json.loads(body)
        if 'error' in d:
            d['errors'] = d['error']
            del d['error']
        body = json.dumps(d)
        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response
