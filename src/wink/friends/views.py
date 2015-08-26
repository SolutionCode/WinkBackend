import re

from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.response import Response
from rest_framework.views import APIView

from helpers.errors import Error, ErrorType
from helpers.authentication import check_authorization
from friends.serializers import FriendOnlyFriendsSerializer
from friends.models import Friend


class Friends(APIView):
    '''
    Class for handling /friends endpoint
    '''

    def get(self, request):
        #Checking if user is authorized
        error = check_authorization(request)
        print request.user.id
        if error is not None:
            return error

        response_dict = {}

        try:
            #Getting sort and page parameters
            sort = request.GET['sort']
            page = request.GET['page']
            page_number = int(page)
        except Exception:
            error = Error(ErrorType.bad_parameters)
            return Response(data=error.__dict__, status=400)

        #get sorting command for order_by
        sorting_command = self.get_sorting_command(sort)

        #getting friend list
        friends_of_current_user = Friend.objects.filter(user = request.user.id).order_by(sorting_command)

        #pagination
        if friends_of_current_user.count() > 0:
            paginator = Paginator(friends_of_current_user, 10)
            try:
                page_of_friends = paginator.page(page_number)
            except PageNotAnInteger:
                page_of_friends = paginator.page(1)
            except EmptyPage:
                page_of_friends = paginator.page(paginator.num_pages)

            #forging answer
            response_dict['data'] = []
            for friend in page_of_friends.object_list:
                response_dict['data'].append(FriendOnlyFriendsSerializer(friend).data)

        return Response(response_dict, status=200)

    def post(self, request):
        #Checking if user is authorized
        error = check_authorization(request)
        if error is not None:
            return error

        #checking if requested user id is valid integer
        requested_user_id = int(request.data['user_id'])

        if requested_user_id is not None:

            #Checking if user exist
            requested_user = User.objects.filter(id=requested_user_id)
            if requested_user.count() > 0:

                #Checking if current user has requested user in his/her friend list
                user_friends = Friend.objects.filter(user = request.user.id, friend = requested_user_id)

                if user_friends.count() > 0:
                    #User is already on friend list
                    error = Error(ErrorType.users_already_friends)
                    return Response(data=error.__dict__, status=409)
                else:
                    #User is not in friend list
                    self.add_friend(request.user, User.objects.get(id=requested_user_id))
                    return Response(status=200)
        error = Error(ErrorType.bad_request)
        return Response(data = error.__dict__, status = 400)



    def add_friend(user, friend):
        friend_entry = Friend()
        friend_entry.user = user
        friend_entry.friend = friend
        friend.save()

    def get_sorting_command(self, sort_string):
        sorting_type_match = re.match('^username$|^date_added$|^first_name$', sort_string)
        if sorting_type_match is not None:
            sorting_type = sorting_type_match.group(0)
        else:
            sorting_type = 'username'

        #selecting sorting type
        if sorting_type == 'username':
            sorting_command = 'friend__username'
        if sorting_type == 'date_added':
            sorting_command = 'date_added'
        if sorting_type == 'first_name':
            sorting_command = 'friend__first_name'

        return sorting_command

