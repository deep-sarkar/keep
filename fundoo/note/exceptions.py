from util.status import response_code

class MyBaseException(Exception):
    def __init__(self,msg,code):
        self.code = code
        self.msg = msg

class RequestObjectDoesNotExixts(MyBaseException):
    pass