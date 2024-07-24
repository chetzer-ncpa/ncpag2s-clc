.. _overview:


========
Overview
========

The **ncpag2s-clc** package provides a convenient command-line interface for retrieving data from the NCPA-G2S system.  Prior to development, data retrieval required filling in multiple web forms and waiting for a batch process to complete and a download link to be sent by email.  Now, data requests can be submitted directly (and anonymously) to the server, which will fulfill them synchronously.

------------
Installation
------------

Just download the code tree from its GitHub repository_ and optionally add the root directory of the repository to your PATH. No additional packages are required.

.. _repository: https://github.com/chetzer-ncpa/ncpag2s-clc


---------
Operation
---------

The client is operated through the **``ncpag2s.py``** script, with the first argument being the subcommand and subsequent arguments being the flags and options necessary. The client will parse the arguments, generate and submit the necessary HTTP requests, and format the responses as requested.  Subcommands can be listed by running ``ncpag2s.py help``, with more detailed help text available for each subcommand from ``ncpag2s.py help [subcommand]``.  Options and flags will vary between subcommands but will be consistent when the meaning is roughly the same.

------
Output
------

Output is ASCII text and can be specified in JSON or NCPAprop format.  Grid requests may also be output in InfraGA format.

-------------
Quick Example
-------------

With ``ncpag2s.py`` in your path, enter:

``ncpag2s.py point --date 2023-07-04 --hour 12 --lat 37.867 --lon -122.259``

All request commands will be in similar formats, with the switchboard program ``ncpag2s.py``, the subcommand (in this case ``point``), and flags following.

