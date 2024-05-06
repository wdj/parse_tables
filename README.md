
Python code for Parsing TaBiThA Tables
=======================================

Description
-----------

This code parses all .mdb tables relevant to the Generate process that are contained in the mylanguage.mdb file.

This is a work in progress; some details may not be complete or correct.

The parsing code for any specific table named "mytable" would be found in the file mytable.py with a relevant class definition.
Each such class has an "import" function to parse a string representing a table to make a data structure, and an "export" function to reproduce the original string.

Usage (MacOS)
-------------

- Install Python 3.7 or higher.
- Install homebrew
- brew install mdbtools
- Run mdb2csv.bash to convert required .mdb files to .csv
- run ./tester with this csv directory.

