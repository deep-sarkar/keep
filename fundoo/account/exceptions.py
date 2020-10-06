 
class MyBaseException(Exception):
    def __init__(self,msg,code):
        self.code = code
        self.msg = msg

class UsernameAlreadyExistsError(MyBaseException):
    pass
        
class EmailAlreadyExistsError(MyBaseException):
    pass

class PasswordDidntMatched(MyBaseException):
    pass

class PasswordPatternMatchError(MyBaseException):
    pass

class UsernameDoesNotExistsError(MyBaseException):
    pass

class EmailDoesNotExistsError(MyBaseException):
    pass