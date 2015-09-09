from collections import OrderedDict

from rest_framework import renderers


class JSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        try:
            resource_name = renderer_context.get('view').serializer_class.resource_name
        except AttributeError:
            resource_name = object

        if 'errors' not in data:
            if 'results' in data:
                objects = data['results']
                del data['results']
                pagination = data
                data = {
                    'data': {
                        resource_name: objects,
                        'pagination': pagination
                    }
                }
            else:
                data = {
                    'data': {
                        resource_name: data
                    }
                }

        response = super(JSONRenderer, self).render(data, accepted_media_type, renderer_context)
        return response
