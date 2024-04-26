# ncpa_geographic.py
#
# Contains classes and functions for performing geographic calculations
#
# Classes:
#   Location:  Associates a latitude, longitude, and optional name
#     Usage:
#       loc = Location( lat, lon )
#       loc = Location( lat, lon, name )
#       lat = loc.lat
#
# Functions:
#   gc = GreatCircle( lat1, lon1, lat2, lon2, N )
#       Returns an array of N evenly-spaced Locations along the great
#       circle path from (lat1,lon1) to (lat2,lon2).  Raises an Exception
#       if the supplied coordinates are antipodes
#   nlonrad = NormalizeLongitude( lonrad )
#       Normalizes a longitide (given in radians) to the range [-pi,pi]


import math

# convenience class for associating a latitude, longitude, and optional name
class Location:
    def __init__(self, lat, lon, name=None):
        self.lat = lat
        self.lon = lon
        self.name = name
        
    @property
    def latitude(self):
        return self.lat
    
    @property
    def longitude(self):
        return self.lon
        
    def __str__(self):
        return f'{self.name + ": " if self.name else ""}[ {self.lat:0.5f}, {self.lon:0.5f} ]' 

# Normalizes a longitude to the range [-pi,pi]
def NormalizeLongitude( lon ):
    out = lon
    while (out > math.pi):
        out -= 2*math.pi
    while (out < -math.pi):
        out += 2*math.pi
    return out


# Computes N points along the great circle path between (lat1,lon1) and (lat2,lon2).
# The code comes from the technique given at https://en.wikipedia.org/wiki/Great-circle_navigation
# using formulas for spherical triangles and Napier's rules.
def GreatCircle( lat1, lon1, lat2, lon2, N ):
    
    path = []
    
    # radius of the earth
    Re = 6371
    
    # check for antipodes
    if (lat1 == -lat2 and lon1 == -lon2):
        raise Exception( "Cannot compute great circle path for antipodes" )
    if (lat1 == lat2 and lon1 == lon2):
        # special case, starting point and end point are the same, return single point
        path.append( Location( lat1, lon1 ) )
        return path
    
    # set up convenience variables and convert to radians
    phi_1 = math.radians( lat1 )
    lambda_1 = NormalizeLongitude( math.radians( lon1 ) )
    phi_2 = math.radians( lat2 )
    lambda_2 = NormalizeLongitude( math.radians( lon2 ) )
    
    # longitude difference
    lambda_12 = NormalizeLongitude( lambda_2 - lambda_1 )
    
    # azimuths at beginning and ending points.
    alpha_1 = math.atan2( 
        math.cos(phi_2)*math.sin(lambda_12),
        math.cos(phi_1)*math.sin(phi_2) - math.sin(phi_1)*math.cos(phi_2)*math.cos(lambda_12)
    )
    alpha_2 = math.atan2(
        math.cos(phi_1)*math.sin(lambda_12),
        -math.cos(phi_2)*math.sin(phi_1) + math.sin(phi_2)*math.cos(phi_1)*math.cos(lambda_12)
    )
    
    # angular distance
    sigma_12 = math.atan2(
        math.sqrt(
            math.pow(
                math.cos(phi_1)*math.sin(phi_2) - math.sin(phi_1)*math.cos(phi_2)*math.cos(lambda_12),
                2
            ) + math.pow(
                math.cos(phi_2)*math.sin(lambda_12),
                2
            )
        ),
        math.sin(phi_1)*math.sin(phi_2) + math.cos(phi_1)*math.cos(phi_2)*math.cos(lambda_12)
    )
    
    # geographic distance
    s_12 = Re * sigma_12
    
    # for points along the great circle we extrapolate the path back to the equator
    # this is called the "node point", point 0
    
    # azimuth at the equator
    alpha_0 = math.atan2(
        math.sin(alpha_1)*math.cos(phi_1),
        math.sqrt(
            math.pow(math.cos(alpha_1), 2) 
            + math.pow(math.sin(alpha_1),2)*math.pow(math.sin(phi_1),2)
        )
    )
    
    # angular distance from the equator to point 1
    if (phi_1 == 0 and alpha_1 == (math.pi / 2)):
        sigma_01 = 0
    else:
        sigma_01 = math.atan2( math.tan( phi_1 ), math.cos(alpha_1) )
    
    # angular distance from equator to point 2
    sigma_02 = sigma_01 + sigma_12
    
    # longitude difference between node and point 1
    lambda_01 = math.atan2(
        math.sin(alpha_0)*math.sin(sigma_01), 
        math.cos(sigma_01)
    )
    
    # longitude of node point
    lambda_0 = NormalizeLongitude( lambda_1 - lambda_01 )
    
    # Now we calculate the set of points along the great circle path
    path.append( Location( lat1, lon1 ))
    for n in range(1,N-1):
        # angular distance of point n from node point
        sigma_n = sigma_01 + n * sigma_12 / (N-1)
        
        # latitude of point n
        phi_n = math.atan2(
            math.cos(alpha_0)*math.sin(sigma_n),
            math.sqrt(
                math.pow(math.cos(sigma_n),2) + 
                math.pow(math.sin(alpha_0),2)*math.pow(math.sin(sigma_n),2)
            )
        )
        
        # longitude of point n
        lambda_n = NormalizeLongitude( 
            math.atan2(
                math.sin(alpha_0)*math.sin(sigma_n),
                math.cos(sigma_n)
            ) + lambda_0
        )
        
        # azimuth at point n
        alpha_n = math.tan( alpha_0 ) / math.cos( sigma_n )
        
        # add it to the path
        path.append( Location( math.degrees( phi_n ), math.degrees( lambda_n ) ) )
        
    # tack on the end point
    path.append( Location( lat2, lon2 ) )
    return path
    

def AngularDistanceInRadians( lat1, lon1, lat2, lon2 ):
    
    # check for antipodes
    if (lat1 == -lat2 and lon1 == -lon2):
        return math.pi
    if (lat1 == lat2 and lon1 == lon2):
        # special case, starting point and end point are the same, return single point
        return 0.0

    # set up convenience variables and convert to radians
    phi_1 = math.radians( lat1 )
    lambda_1 = NormalizeLongitude( math.radians( lon1 ) )
    phi_2 = math.radians( lat2 )
    lambda_2 = NormalizeLongitude( math.radians( lon2 ) )

    # longitude difference
    lambda_12 = NormalizeLongitude( lambda_2 - lambda_1 )

    # azimuths at beginning and ending points.
    alpha_1 = math.atan2(
        math.cos(phi_2)*math.sin(lambda_12),
        math.cos(phi_1)*math.sin(phi_2) - math.sin(phi_1)*math.cos(phi_2)*math.cos(lambda_12)
    )
    alpha_2 = math.atan2(
        math.cos(phi_1)*math.sin(lambda_12),
        -math.cos(phi_2)*math.sin(phi_1) + math.sin(phi_2)*math.cos(phi_1)*math.cos(lambda_12)
    )

    # angular distance
    sigma_12 = math.atan2(
        math.sqrt(
            math.pow(
                math.cos(phi_1)*math.sin(phi_2) - math.sin(phi_1)*math.cos(phi_2)*math.cos(lambda_12),
                2
            ) + math.pow(
                math.cos(phi_2)*math.sin(lambda_12),
                2
            )
        ),
        math.sin(phi_1)*math.sin(phi_2) + math.cos(phi_1)*math.cos(phi_2)*math.cos(lambda_12)
    )

    return sigma_12

def GeographicDistance( lat1, lon1, lat2, lon2 ):
    Re = 6371
    return Re * AngularDistanceInRadians( lat1, lon1, lat2, lon2 )


