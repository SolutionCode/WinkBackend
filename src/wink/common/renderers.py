from rest_framework import renderers


class JSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        try:
            resource_name = renderer_context.get('view').serializer_class.resource_name
        except AttributeError:
            # TODO: verify it's working... what is object when called
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
                if resource_name:
                    data = {
                        'data': {
                            resource_name: data
                        }
                    }
                else:
                    # special case for EmptySerializer, Register by social token
                    data = {
                        'data': data
                    }

        response = super(JSONRenderer, self).render(data, accepted_media_type, renderer_context)
        return response
