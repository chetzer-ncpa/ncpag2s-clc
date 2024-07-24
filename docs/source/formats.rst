.. _formats:

============
Data Formats
============

-----------
JSON Format
-----------

The default JSON format contains a "metadata" structure, a "data" structure containing one or more "parameter" structures, and some bookkeeping entries at the end.  In more detail, the format is structured as follows:

**Individual Profiles**

An example of a single G2S profile in JSON format is shown here::

  {
    "metadata": {
        "sourcefile": "G2SGCSB2023012404.bin",
        "nz": 1501,
        "time": {
            "datetime": "2023-01-24T04:00:00",
            "format": "%Y-%m-%dT%H:%M:%S",
            "__extended_json_type__": "datetime"
        },
        "location": {
            "latitude": 19.59,
            "longitude": -155.89,
            "__extended_json_type__": "Location"
        },
        "parameters": 7
    },
    "data": [
            {
                "parameter": "Z0",
                "description": "Ground Height",
                "units": "km",
                "n": 1,
                "values": [
                    1.052
                ]
            },
            {
                "parameter": "Z",
                "description": "Height",
                "units": "km",
                "n": 1501,
                "values": [
                    0.0,
                    0.1,
                    ...

etc.

JSON files containing multiple profiles will generally be organized into profile sets, which may be ``line``s, ``grid``s, or other logical groupings.  In these cases there will be an outer JSON block with its own metadata structure, which will vary by the type of grouping.  So a ``line`` grouping might look like this::

  {
    "metadata": {
        "type": "line",
        "points": 21,
        "reference_location": {
            "latitude": 19.59,
            "longitude": -155.89,
            "__extended_json_type__": "Location"
        },
    },
    "points": [
        {
        <individual profile structure>
        },
        {
        <individual profile structure>
        },

etc.  In these cases, additional fields will often be added to the metadata block for each constituent profile as appropriate; for example in the case of the line above, each profile's metadata block will also have a "range" entry with the distance to the reference location in km.

This nesting behavior is extended as needed. For example if lines are requested for multiple times, the individual lines will be presented as a comma-separated series of the above structure, enclosed within square brackets.  

---------------
NCPAprop Format
---------------

This is the format used by the ncpaprop_ package.  It consists of a series of comments, interspersed with formatted header lines that describe the data structure, followed by a set of space-separated columns of ASCII data, one column per atmospheric property.  An example of the format would be::

	# Data Source: G2SGCSB2023070412.bin
	# Model Time 2023-07-04T12:00:00
	# Location = [ 37.8670, -122.2590 ]
	# Fields = [ Z(km), T(K), U(m/s), V(m/s), R(g/cm3), P(mbar) ]
	# Ground Height = 0.076 km
	# The following lines are formatted input for ncpaprop
	#% 0, Z0, km, 0.076
	#% 1, Z, km
	#% 2, T, K
	#% 3, U, m/s
	#% 4, V, m/s
	#% 5, RHO, g/cm3
	#% 6, P, mbar
	  0.000      2.85880e+02       1.40070e+00       1.26130e+00       1.23280e-03       1.01150e+03
	  0.100      2.85530e+02       1.59140e+00       1.33830e+00       1.21970e-03       9.99540e+02
	  0.200      2.85200e+02       1.78140e+00       1.41670e+00       1.20670e-03       9.87710e+02
	  0.300      2.85250e+02       1.95350e+00       1.53070e+00       1.19220e-03       9.76030e+02
	  0.400      2.86050e+02       2.09570e+00       1.67470e+00       1.17480e-03       9.64500e+02
	...

etc.  In this example there are 6 columns of data.  The formatted header lines beginning with ``#%`` associate the column number with a label and its units.  Header lines with column number 0 indicate scalar quantities associated with the profile overall.

Because this format was designed for single-location profiles only, multi-profile requests have their own formats.  Line requests are output as a directory ``profiles`` containing a series of single-profile files, one per point, and a summary file associating each profile with its distance from the beginning of the line.  Grid requests are returned similarly, except the summary file associates each profile with its latitude/longitude coordinates. 

--------------
InfraGA Format
--------------

This data format is available for grid requests only and is intended to work with the range-dependent modules of the LANL InfraGA_ geometric acoustics package.  It is similar to the ``ncpaprop`` format, except that two summary files are created, one with the latitude points and one with the longitude points, and the filename structure is changed to that expected by the range-dependent InfraGA modules.  A third file ``flags.txt`` is also generated, providing the flags to use with InfraGA in order to read the grid files.
 

.. _ncpaprop: https://github.com/chetzer-ncpa/ncpaprop-release
.. _InfraGA: https://github.com/LANL-Seismoacoustics/infraGA