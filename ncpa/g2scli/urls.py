from ncpa.g2scli.settings import config
import copy

def format_url(urltype, time=None, *args, **kwargs):
    
    params = copy.deepcopy(kwargs)
    if time:
        for key in ('year','month','day','hour'):
            params[key] = getattr(time,key)
                
    pattern = config['urls'].get(urltype)
    if pattern:
        return pattern.format(**params)
    else:
        raise KeyError(f'URL pattern not found for urltype={urltype}')


        