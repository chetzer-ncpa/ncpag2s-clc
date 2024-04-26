from datetime import datetime, timedelta, timezone, date, time
import logging


def add_date_arguments(parser, single=True, requiresingle=False, multiple=True, requiremultiple=False):
    plural = '(s)' if multiple else ''
    if single:
        parser.add_argument(
            "--date", nargs='*' if multiple else 1, default=[], required=requiresingle, type=str, help=f"UTC date{plural} in any ISO8601 format"
        )
        parser.add_argument(
            "--hour", nargs='*' if multiple else 1, default=[], required=requiresingle, type=int, help=f"UTC hour{plural}"
        )
    
    if multiple:
        parser.add_argument(
            '--startdate', nargs='?', default=None, required=requiremultiple, type=str, help='Starting date for regular sequence, in any ISO8601 format'
        )
        parser.add_argument(
            '--starthour', nargs='?', default=None, required=requiremultiple, type=int, help='Starting hour for regular sequence'
        )
        parser.add_argument(
            '--every', nargs='?', default=None, required=requiremultiple, type=int, help='Interval in hours for regular sequence'
        )
        parser.add_argument(
            '--enddate', nargs='?', default=None, required=requiremultiple, type=str, help='Ending date for regular sequence, in any ISO8601 format'
        )
        parser.add_argument(
            '--endhour', nargs='?', default=None, required=requiremultiple, type=int, help='Ending hour for regular sequence'
        )

def add_point_location_arguments(parser, required=True ):
    parser.add_argument(
        '--latitude', nargs=1, default=[], required=required, type=float, help='Latitude for point'
    )
    parser.add_argument(
        '--longitude', nargs=1, default=[], required=required, type=float, help='Longitude for point'
    )
    return parser
        
def add_line_location_arguments(parser, required=True ):
    parser.add_argument(
        '--startlatitude', nargs='?', default=None, required=required, type=float, help='Latitude of start point'
    )
    parser.add_argument(
        '--startlongitude', nargs='?', default=None, required=required, type=float, help='Longitude of start point'
    )
    parser.add_argument(
        '--endlatitude', nargs='?', default=None, required=required, type=float, help='Latitude of end point'
    )
    parser.add_argument(
        '--endlongitude', nargs='?', default=None, required=required, type=float, help='Longitude of end point'
    )
    parser.add_argument(
        '--points', nargs='?', default=None, required=required, type=int, help='Number of points in line'
    )
    return parser

def parse_datetimes(options):
    # First, check for specified dates and hours, these take precedence
    dates = [date.fromisoformat(ds) for ds in options.get('date',[])]
    hours = options.get('hour',[])
    
    datetimes = []
    if dates and hours:
        for d in dates:
            for h in hours:
                datetimes.append(datetime.combine(d,time(hour=h),timezone.utc))
    else:
        try:
            interval = timedelta(hours=options.get('every'))
            starttime = datetime.combine(date.fromisoformat(options.get('startdate',None)), time(hour=options.get('starthour',None)), timezone.utc)
            endtime = datetime.combine(date.fromisoformat(options.get('enddate',None)), time(hour=options.get('endhour',None)), timezone.utc)
            
            while starttime <= endtime:
                datetimes.append(starttime)
                starttime += interval
        
        except TypeError:
            pass
        
    return datetimes
            
            
            
            
            
        