from datetime import date, datetime, timezone, timedelta


class JulianDate():
    
    def __init__(self,jdate=None):
        if jdate is None:
            self.jdate = None
        elif type(jdate) == datetime:
            self.jdate = jdate.replace(tzinfo=timezone.utc)
        elif type(jdate) == date:
            self.jdate = datetime(jdate.year,jdate.month,jdate.day,0,0,0,
                             tzinfo=timezone.utc)
        elif type(jdate) == str:
            if len(jdate) == 7:
                year = int(jdate[0:4])
                doy = int(jdate[4:7])
                self.jdate = datetime(year,1,1,0,0,0,tzinfo=timezone.utc)
                self.jdate += timedelta(days=(doy-1))
            else:
                self.jdate = to_datetime(jdate)
        elif type(jdate) == int:
            # do some fancy parsing
            istr = str(jdate)
            doy = int(istr[-3:])
            year = int(jdate/1000)
            self.jdate = datetime(year,1,1,0,0,0,tzinfo=timezone.utc)
            self.jdate += timedelta(days=(doy-1))
        else:
            raise TypeError(f"Unsupported type for jdate argument: {jdate}")
    
    def __int__(self):
        if self.jdate is None:
            return -1
        else:
            return int(self.jdate.strftime("%Y%j"))
        
    def __str__(self):
        return str(int(self))
        
def to_datetime(v,makeaware=True,tz=timezone.utc):
    if v is None:
        return None
    
    # test various types
    tv = type(v)
    if tv == datetime:
        # v is a datetime object already, just copy it
        dt = datetime.fromtimestamp(v.timestamp(),
                                               tz=v.tzinfo)
        if makeaware and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
    elif tv == datetime.date:
        # v is a date object, need to add the time info
        dt = datetime.fromtimestamp(v.timestamp())
        if makeaware:
            dt = dt.replace(tzinfo=tz)
    elif tv == str:
        # v is a string, try to parse it
        v = v.strip()
        if v == "":
            return None
        dt = datetime.fromisoformat(v)
        if makeaware and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
    elif tv == float or tv == int:
        # v is a number, treat it as a unix epoch time
        if makeaware:
            dt = datetime.fromtimestamp(v,tz=tz)
        else:
            dt = datetime.fromtimestamp(v)
    else:
        raise NotImplementedError(f"Type {tv} not supported")
    return dt

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