import json
from datetime import datetime

'''
ExtendedEncoder and ExtendedDecoder adapted from https://mathspp.com/blog/custom-json-encoder-and-decoder
'''

class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        name = type(obj).__name__
        try:
            encoder = getattr(self, f'encode_{name}')
        except AttributeError:
            super().default(obj)
        else:
            encoded = encoder(obj)
            encoded['__extended_json_type__'] = name
            return encoded
        
class ExtendedDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        kwargs["object_hook"] = self.object_hook
        super().__init__(**kwargs)

    def object_hook(self, obj):
        try:
            name = obj["__extended_json_type__"]
            decoder = getattr(self, f"decode_{name}")
        except (KeyError, AttributeError):
            return obj
        else:
            return decoder(obj)
        
class RoundingEncoder(ExtendedEncoder):
    def __init__(self,sigfigs=0,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.sigfigs = sigfigs
        
    def roundfloat(self,f):
        if self.sigfigs:
            return float(f'{f:0.{self.sigfigs-1}e}')
        else:
            return f
        
    def default(self,obj):
        if self.sigfigs: 
            if type(obj).__name__ == 'float':
                return super().default(self.roundfloat(obj))
            elif type(obj).__name__ == 'list':
                fobj = []
                for f in obj:
                    if type(f).__name__ == 'float':
                        fobj.append(self.roundfloat(f))
                    else:
                        fobj.append(f)
                return super().default(fobj)
        return super().default(obj)