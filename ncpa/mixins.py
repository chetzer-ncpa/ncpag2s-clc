

class Dictable:
    def __init__(self,*args,**kwargs):
        pass
    
    def as_dict(self):
        raise NotImplementedError
    
    def __iter__(self):
        d = self.as_dict()
        for key in d.keys():
            yield (key, d[key])

class HasMetadata:
    def __init__(self,*args,**kwargs):
        self.metadata = {}
        
    def clear_metadata(self):
        self.metadata = {}
    
    def set_metadata(self,key,val):
        self.metadata[key] = val
        
    def get_metadata(self,key):
        try:
            return self.metadata[key]
        except KeyError:
            return None
        
    def increment_metadata(self,key):
        self.metadata[key] += 1