from datetime import datetime, timezone, timedelta





def parseutctime(dtstr):
    return datetime.fromisoformat(dtstr).replace(tzinfo=timezone.utc)

def roundtime(t,nearest):
    if nearest == 'day':
        return t.replace(hour=0,minute=0,second=0,microsecond=0)
    elif nearest == 'hour':
        return t.replace(minute=0,second=0,microsecond=0)
    elif nearest == 'minute':
        return t.replace(second=0,microsecond=0)
    elif nearest == 'second':
        return t.replace(microsecond=0)

def utcnow():
    return datetime.now(tz=timezone.utc)