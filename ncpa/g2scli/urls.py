from ncpa.g2scli.settings import config


def format_url(urltype, *args, **kwargs):
    pattern = config['urls'].get(urltype)
    if pattern:
        return pattern.format(**kwargs)
    else:
        raise KeyError(f'URL pattern not found for urltype={urltype}')
 