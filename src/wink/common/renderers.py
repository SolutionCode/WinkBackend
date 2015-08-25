from rest_framework import renderers


class JSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'errors' not in data:
            data = {'data': data}

        response = super(JSONRenderer, self).render(data, accepted_media_type, renderer_context)
        return response
