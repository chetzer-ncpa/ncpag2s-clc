


class G2SError(BaseException):
    pass

class NoGridfileExistsError(G2SError):
    def __init__(self,time=None,*args,**kwargs):
        self.time = time
        timestr = ''
        if self.time:
            timestr = ' for {self.time}'
        super().__init__(f'NoGridfileExists: No gridfile was found{timestr}')
        
class GridfileDoesNotExistError(G2SError):
    def __init__(self,filename,*args,**kwargs):
        self.filename = filename
        super().__init__(f'{self.filename} does not exist',*args,**kwargs)
        
class GridfileNotReadableError(G2SError):
    def __init__(self,filename,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.filename = filename
        
    def __str__(self):
        return f'Gridfile {self.filename} not readable'
    
class BadProfileError(G2SError):
    pass
        