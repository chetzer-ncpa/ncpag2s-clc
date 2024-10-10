.. _userguide:

==========
User Guide
==========

This section will go into greater detail about the use of the various available subcommands and their flags.  Each subcommand has help text that can be accessed with ``ncpag2s.py help [subcommand]``.

----------------
Time Conventions
----------------

G2S data is generally available hourly after 1 January 2011, and every 6 hours between 1 January 2003 and 31 December 2010.  Thus, there is no reason to specify times to any precision greater than 1 hour.  In all cases, subcommands require dates and times to be specified, either singly or as a range.  In each case, dates and hours are specified separately.  Dates can be in any ISO8601-compliant format (e.g. 2023-08-01) while hours are specified as integers from 0-23.  All times are in UTC.

--------------
Output Formats
--------------

In all cases, ``json`` and ``ncpaprop`` outputs are available.  Others may be available for specific subcommands.  For details on these formats, see Data Formats.

----------------------------------------
``checktime``: Confirm data availability
----------------------------------------

This subcommand queries the G2S database to verify that data is available for the date and time requested.  The command will return either "Time \[datetime\] is available" or "Time \[datetime\] is not available".

Usage is:

``ncpag2s.py checktime --date [date] --hour [hour]``

where ``[flags]`` is one or more of the following, with flags that require each other grouped together:

**Required:**
``--date [date]``
``--hour [hour]``
	The UTC date and hour for the grid file.
	
**Example Command**
	``ncpag2s.py checktime --date 2023-08-01 --hour 8``
	
	``ncpag2s.py checktime --date 2008-08-01 --hour 8``
	



------------------------------------
``point``: A single geographic point
------------------------------------

This subcommand will extract profile(s) at one or more times at a single geographic point (i.e. one latitude/longitude pair).  Usage is:

``ncpag2s.py point [flags]``

where ``[flags]`` is one or more of the following, with flags that require each other grouped together:

**Required:**

``--latitude [latitude]``
``--longitude [longitude]``
	The latitude/longitude coordinates at which to extract the profile.  Coordinates are expected to be in the ranges \[-90,90\] and \[-180,180\], respectively.


**One of the following groups is required:**

``--date [date]``
``--hour [hour]``
	The UTC date and hour  at which to extract the profile.
	
**OR**

``--startdate [date]``
``--starthour [hour]``
``--enddate [date]``
``--endhour [hour]``
``--every [interval]``
	The starting and ending dates and times for a range of multiple times, extracted at the requested interval (in hours).
	
**Optional:**

``--outputformat [json|ncpaprop]``
	Specifies the format in which the profile(s) are output.  The default is ``json``.
	
``--output [destination]``
	The destination for the output data.  The default is to print to the screen.  For ``json`` output this should be a file.  For ``ncpaprop`` output this should be a file for single-time requests, or a directory for multi-time requests.

**Example Commands**
	``ncpag2s.py point --date 2023-07-04 --hour 12 --lat 37.867 --lon -122.259``

	``ncpag2s.py point --date 2023-07-04 --hour 12 --lat 37.867 --lon -122.259 --outputformat ncpaprop --output rasputin.dat``
	

-----------------------------------------
``line``: An evenly-spaced line of points
-----------------------------------------

This subcommand will extract an evenly-spaced great-circle line of profiles between two latitude/longitude pairs at one or more times.  Usage is:

``ncpag2s.py line [flags]``

where ``[flags]`` is one or more of the following, with flags that require each other grouped together:

**Required:**

``--startlatitude [latitude]``
``--startlongitude [longitude]``
``--endlatitude [latitude]``
``--endlongitude [longitude]``
	The starting and ending latitude/longitude coordinates of the great-circle line.  Coordinates are expected to be in the ranges \[-90,90\] and \[-180,180\], respectively.
	
``--points``
	The number of points to extract in the line.

**One of the following groups is required:**

``--date [date]``
``--hour [hour]``
	The UTC date and hour  at which to extract the profile.
	
**OR**

``--startdate [date]``
``--starthour [hour]``
``--enddate [date]``
``--endhour [hour]``
``--every [interval]``
	The starting and ending dates and times for a range of multiple times, extracted at the requested interval (in hours).
	
**Optional:**

``--outputformat [json|ncpaprop]``
	Specifies the format in which the profile(s) are output.  The default is ``json``.
	
``--output [destination]``
	The destination for the output data.  The default is to print to the screen.  For ``json`` output this should be a file.  For ``ncpaprop`` output this should be a directory.

**Example Commands**
	``ncpag2s.py line --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 --endlat 35.23 --endlon -106.66 --points 21``
	
	``ncpag2s.py line --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 --endlat 35.23 --endlon -106.66 --points 21 --outputformat ncpaprop --output /tmp/ms_to_abq``

-----------------------------------------
``grid``: An evenly-spaced grid of points
-----------------------------------------

This subcommand will extract an evenly-spaced grid of profiles in Mercator projection (i.e. evenly-spaced latitude and longitude intervals, not necessarily in physical distance).  Usage is:

``ncpag2s.py grid [flags]``

where ``[flags]`` is one or more of the following, with flags that require each other grouped together:

**Required:**

``--startlatitude [latitude]``
``--startlongitude [longitude]``
``--endlatitude [latitude]``
``--endlongitude [longitude]``
	The starting and ending latitude/longitude coordinates of the grid.  These will correspond to the lower-left (i.e. southwesternmost) and upper-right (i.e. northeasternmost) corners of the grid, respectively.  Coordinates are expected to be in the ranges \[-90,90\] and \[-180,180\], respectively.
	
``--latpoints``
``--lonpoints``
	The number of latitude and longitude points to extract in the grid.

**One of the following groups is required:**

``--date [date]``
``--hour [hour]``
	The UTC date and hour  at which to extract the profile.
	
**OR**

``--startdate [date]``
``--starthour [hour]``
``--enddate [date]``
``--endhour [hour]``
``--every [interval]``
	The starting and ending dates and times for a range of multiple times, extracted at the requested interval (in hours).
	
**Optional:**

``--outputformat [json|ncpaprop|infraga]``
	Specifies the format in which the profile(s) are output.  The default is ``json``.
	
``--output [destination]``
	The destination for the output data.  The default is to print to the screen.  For ``json`` output this should be a file.  For ``ncpaprop`` or ``infraga`` output this should be a directory.

**Example Commands**
	``ncpag2s.py grid --date 2023-08-10 --hour 0 --startlat 34.0 --startlon -89.0 --endlat 40.0 --endlon -96.0 --latpoints 13 --lonpoints 15``
	
	``ncpag2s.py grid --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 --endlat 35.23 --endlon -106.66 --points 21 --outputformat infraga --output /tmp/testgrid``


-----------------------------------
``raw``: A raw G2S coefficient file
-----------------------------------

This subcommand will return a raw G2S coefficient file, for use if you are authorized to possess the G2S extraction software.  Usage is:

``ncpag2s.py raw [flags]``

where ``[flags]`` is one or more of the following, with flags that require each other grouped together:

**Required:**
``--date [date]``
``--hour [hour]``
	The UTC date and hour for the grid file.
	
**Optional:**

``--outputfile [filename]``
	Write the coefficients to this filename.  Default will let the server decide.
	
**Example Command**
	``ncpag2s.py raw --date 2023-07-04 --hour 12 --outputfile tester.bin``
	