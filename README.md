# NCPAG2S Command-Line Client

## Installation
Just download and optionally place the root directory of the repository in your PATH.  No additional packages are required.

## Operation
The client is operated through the **ncpag2s.py** script, with the first argument being the subcommand and subsequent arguments being the flags and options necessary.  The client will parse the arguments, generate and submit the necessary HTTP requests, and format the responses as requested.

Subcommands can be listed by running `ncpag2s.py help`, with more detailed help text available for each subcommand from `ncpag2s.py help [subcommand]`.

Options and flags will vary between subcommands but will be consistent when the meaning is roughly the same.  Generally speaking, they will fall into the following categories:

### Time
The time(s) at which data is to be returned are indicated using `--date` and `--hour` flags.  Dates can be parsed from any ISO8601-compliant format; examples will be formatted as YYYY-MM-DD.  Times are treated as integer hours, UTC.  When supported, multiple dates and/or hours can be provided after the flags, in which case every combination of date and hour will be retrieved.  Multi-time requests can be slow to complete, as each date/time requires a separate request be sent to the server.

### Location
Locations are specified as latitude and longitude in decimal degrees.  Different subcommands will require different sets of options, see the help texts for details.

### Output
Output destinations and formats can be specified with `--output` and `--outputformat` flags, respectively.  By default, retrieved profiles will print to the terminal, where they can be redirected if desired.  Alternately, the `--output` flag can be used to specify a file or directory to use for output, as appropriate for the chosen format.

Currently two output formats are supported.  **ncpaprop** format returns profiles in the custom format used by the [**ncpaprop**](https://github.com/chetzer-ncpa/ncpaprop-release/) propagation package, but is limited to one profile per file; multi-profile formats requested in **ncpaprop** format require that `--output` be used to specify a directory where the returned files and directories will be written.  Alternately, a custom JSON format has been developed that supports single profiles as well as multi-location profile sets.  Details of the JSON format are available in the user manual.

Absent specific instructions, the client will default to the following behavior:

- **For JSON requests**:
  **`--output` flag absent:** Output will print to the screen.
  **`--output <filename>`:** Output will be written to the file, truncating any existing contents.
  **`--output <directoryname>`:** Output will be written to a file in the specified directory, with the filename format dependent on the type of request.
- **For NCPAprop requests**
  **`--output` flag absent:** If a single profile is returned, output will print to the screen.  If multiple profiles are returned, output will be written to descriptively-named files in the current directory.
  **`--output <filename>`:** If a single profile is returned, output will be written to the file, truncating any existing contents.  If multiple profiles are returned, an error will be reported.
  **`--output <directoryname>`:** Output will be written to files in the specified directory, with the filename format dependent on the type of request.  In the case of `line` or `grid` requests, a summary file will be created.  The individual profiles will be placed in a subdirectory of the specified directory, which will be created if absent.


## Request Types
The command-line client supports the following types of requests, all of which currently, or will eventually, support multiple times:

- **`point`**: Returns the atmospheric profiles at the single specified location.
- **`line`**: An evenly-spaced line of profiles along the great-circle path between two points.
- **`grid`**: An evenly-spaced grid of profiles between two corner points, assuming Mercator projection.
- **`fan`**: A set of great-circle paths originating at a single point and fanning out over a range of azimuths.
- **`raw`**: The raw G2S coefficient file for a single time.  Note that proprietary software is required to read this file format.  If you don't know what that software is, then you don't have access to it and the raw file will not be of use.

