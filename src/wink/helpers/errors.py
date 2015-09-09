
class ErrorType(object):
    unauthorized = (401, 'This action requires authentication')
    users_already_friends = (409, 'User is already on friends list')
    bad_request = (400, 'Bad or malformed request')
    bad_parameters = (400, 'Bad parameters')
    success = (200, 'Success')

'''
Error scheme:
{
    code : numer bledu HTTP
    message : wiadomosc bledu
}
'''

class Error(object):
    code = None
    message = None

    def __init__(self, type):
        self.code = type[0]
        self.message = type[1]