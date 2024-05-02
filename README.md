# NCPAG2S Command-Line Client

## Installation
Just download and optionally place the root directory of the repository in your PATH.  No additional packages are required.

## Operation
The client is operated through the **ncpag2s.py** script, with the first argument being the subcommand and subsequent arguments being the flags and options necessary.  The client will parse the arguments, generate and submit the necessary HTTP requests, and format the responses as requested.

Subcommands can be listed by running `ncpag2s.py help`, with more detailed help text available for each subcommand from `ncpag2s.py help [subcommand]`.

Options and flags will vary between subcommands but will be consistent when the meaning is roughly the same.  Generally speaking, they will fall into the following categories:

### Time
The time(s) at which data is to be returned are indicated using `--date` and `--hour` flags for single-time requests, or `--startdate`, `--starthour`, `--enddate`, `--endhour`, and `--every` flags for time ranges.  Dates can be parsed from any ISO8601-compliant format; examples will be formatted as YYYY-MM-DD.  Times are treated as integer hours, UTC.  Be aware that multi-time requests are slower to complete than single-time requests, as each date/time requires a separate request be sent to the server.

### Location
Locations are specified as latitude and longitude in decimal degrees.  Different subcommands will require different sets of options, see the help texts for details.

### Output
Output destinations and formats can be specified with `--output` and `--outputformat` flags, respectively.  By default, retrieved profiles will print to the terminal, where they can be redirected if desired.  Alternately, the `--output` flag can be used to specify a file or directory to use for output, as appropriate for the chosen format.

Currently two output formats are supported.  **ncpaprop** format returns profiles in the custom format used by the [**ncpaprop**](https://github.com/chetzer-ncpa/ncpaprop-release/) propagation package, but is limited to one profile per file; multi-profile formats requested in **ncpaprop** format require that `--output` be used to specify a directory where the returned files and directories will be written.  Alternately, a custom JSON format has been developed that supports single profiles as well as multi-location profile sets.  Details of the JSON format are available in the user manual.

Absent specific instructions, the client will default to the following behavior:

- **For JSON requests:**
  
  **`--output` flag absent:** Output will print to the screen.
  
  **`--output <filename>`:** Output will be written to the file, truncating any existing contents.
  
  **`--output <directoryname>`:** Output will be written to a file in the specified directory, with the filename format dependent on the type of request.
  
- **For NCPAprop requests:**
  
  **`--output` flag absent:** If a single profile is returned, output will print to the screen.  If multiple profiles are returned, output will be written to descriptively-named files in the current directory.
  
  **`--output <filename>`:** If a single profile is returned, output will be written to the file, truncating any existing contents.  If multiple profiles are returned, an error will be reported.
  
  **`--output <directoryname>`:** Output will be written to files in the specified directory, with the filename format dependent on the type of request.  In the case of `line` or `grid` requests, a summary file will be created.  The individual profiles will be placed in a subdirectory of the specified directory, which will be created if absent.


## Request Types
The command-line client supports the following types of requests, all of which currently, or will eventually, support multiple times:

- **`point`**: Returns the atmospheric profiles at the single specified location.
- **`line`**: An evenly-spaced line of profiles along the great-circle path between two points.
- **`grid`**: (not yet developed) An evenly-spaced grid of profiles between two corner points, assuming Mercator projection.
- **`fan`**: (not yet developed) A set of great-circle paths originating at a single point and fanning out over a range of azimuths.
- **`raw`**: The raw G2S coefficient file for a single time.  Note that proprietary software is required to read this file format.  If you don't know what that software is, then you don't have access to it and the raw file will not be of use.


## JSON Format
The default JSON format is structured as follows:

### Individual Profiles
An example of an individual G2S profile in JSON format is shown here:

```
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
...etc.
```

JSON files containing multiple profiles will generally be grouped into profile sets, which may be `line`s, `grid`s, or other logical groupings.  In these cases there will be a containing JSON block with its own metadata structure, which will vary by the type of grouping.  An example of a line of profiles along a great-circle path between two points might be:

```
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
...etc
```

In these cases, additional fields will often be added to the metadata block for each constituent profile as appropriate; for example in the case of the line above, each profile's metadata block will also have a "range" entry with the distance to the reference location in km.  

This nesting behavior is extended as needed.  For example if lines are requested for multiple times, the individual lines will be presented as a comma-separated series of the above structure, enclosed within square brackets.

Commands to convert between supported data formats are under development.


## Example Commands
`ncpag2s.py point --date 2023-07-04 --hour 12 --lat 37.867 --lon -122.259`

Retrieve the profile at \[37.867,-122.259\] (Rasputin Records, Berkeley, California) at 1200 UTC on 4 July 2023 in JSON format and print to the screen.

`ncpag2s.py point --date 2023-07-04 --hour 12 --lat 37.867 --lon -122.259 --outputformat ncpaprop --output rasputin.dat`

Retrieve the same profile but in **ncpaprop** format and write to the file `rasputin.dat` instead of to the screen.

`ncpag2s.py line --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 --endlat 35.23 --endlon -106.66 --points 21 --output ms_to_abq.dat`

Retrieve a line of 21 profiles evenly spaced between Oxford, MS and Albuquerque, NM at 00 UTC on 10 August 2023 in JSON format and write to the file `ms_to_abq.dat`.

`ncpag2s.py line --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 --endlat 35.23 --endlon -106.66 --points 21 --outputformat ncpaprop --output /tmp/ms_to_abq`

Retrieve the same line of 21 profiles but write them as a **ncpaprop** `--atmos2d` summary file/profile directory structure to the directory /tmp/ms_to_abq.

`ncpag2s.py line --startlat 19.59 --startlon -155.89 --endlat 29.59 --endlon -155.89 --points 11 --startdate 2023-01-24 --starthour 0 --enddate 2023-01-25 --endhour 0 --every 4`

Retrieve a line of 11 points going 10 degrees due north from the I59US infrasound station, every 4 hours for 24 hours total starting 00 UT on 24 January 2023, output in JSON format to the screen.


