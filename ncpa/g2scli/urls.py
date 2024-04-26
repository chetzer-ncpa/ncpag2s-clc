from ncpa.g2scli.settings import config


def format_url(urltype, time=None, *args, **kwargs):
    if time:
        for key in ('year','month','day','hour'):
            kwargs[key] = getattr(time,key)
                
    pattern = config['urls'].get(urltype)
    if pattern:
        return pattern.format(**kwargs)
    else:
        raise KeyError(f'URL pattern not found for urltype={urltype}')


        