from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.response import Response
from rest_framework.views import APIView

from messages.models import Message
from messages.serializers import BodyDateOnlyMessageSerializer

from helpers.errors import Error, ErrorType
from helpers.authentication import check_authorization

class PostMessage(APIView):
    '''
    Class for sending messages
    '''

    def post(self,request):
        error = check_authorization(request)
        if error is not None:
            return error

        try:
            #Getting sort and page parameters
            body = request.POST['body']
            to = request.POST['to']
            to_id = int(to)
        except Exception:
            error = Error(ErrorType.bad_parameters)
            return Response(data=error.__dict__, status=400)

        requested_user = User.objects.filter(id=to_id)
        if requested_user.count() > 0:
            #Adding new message
            new_message = Message()
            new_message.body = body
            new_message.to_user = to_id
            new_message.from_user = request.user.id
            new_message.save()

            return Response(status=200)

        else:
            #Recipent not found
            error = Error(ErrorType.bad_parameters)
            return Response(data=error.__dict__, status=422)



class GetMessageHistory(APIView):
    '''
    Class for getting message history
    '''
    def get(self, request, id):
        print id
        print request.user.id

        response_dict = {}

        try:
            #Getting sort and page parameters
            page_number = request.GET['page']
        except Exception:
            error = Error(ErrorType.bad_parameters)
            return Response(data=error.__dict__, status=400)

        try:
            timestamp = request.GET['freeze_time']
        except Exception:
            timestamp = None

        if timestamp is None:
            messages = Message.objects.filter(from_user = id, to_user = request.user.id).order_by('created_at')
        else:
            messages = Message.objects.filter(from_user = id, to_user = request.user.id, created_at__gte = timestamp).order_by('created_at')

        paginator = Paginator(messages, 10)
        try:
            page_of_messages = paginator.page(page_number)
        except PageNotAnInteger:
            page_of_messages = paginator.page(1)
        except EmptyPage:
            page_of_messages = paginator.page(paginator.num_pages)

        response_dict['data'] = {}

        response_dict['data']['messages'] = []

        for message in page_of_messages.object_list:
            response_dict['data']['messages'].append(BodyDateOnlyMessageSerializer(message).data)

        return Response(response_dict, status=200)