# Introduction
**TOMES Packager** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to create a TOMES archival information package (AIP) with the following structure:

    [account_id]/
      eaxs/
        attachments/*.*
        xml/
          [account_id].xml
          [account_id]_tagged.xml
      metadata/*.*
      mime/*.*
      pst/
        [account_id].pst
      [account_id].mets.manifest
      [account_id].mets.xml

**??? TODO: ???**

- meant to be used with TOMES workflow.
- doesn't currently support more than one PST
- Metadata/PST/METS are optional.
- Needs a more complete explanation section.

# External Dependencies
TOMES Packager requires the following:

- [Python](https://www.python.org) 3.0+ (using 3.5+)
	- See the "./requirements.txt" file for additional module dependencies.
	- You will also want to install [pip](https://pypi.python.org/pypi/pip) for Python 3.

If you want to use TOMES Packager to create Dublin Core/METS metadata, you will also need Microsoft Office 2007+ or another suite, such as [LibreOffice](https://www.libreoffice.org), capable of creating Excel 2007+ Excel files (.xlsx).

# Installation
After installing the external dependencies above, you'll need to install some required Python packages.

The required packages are listed in the "./requirements.txt" file and can easily be installed via PIP <sup>[1]</sup>: `pip3 install -r requirements.txt`

You should now be able to use TOMES Packager from the command line or as a locally importable Python module.

If you want to install TOMES Packager as a Python package, do: `pip3 install . -r requirements.txt`

Running `pip3 uninstall tomes_packager` will uninstall the TOMES Packager package.

# Unit Tests
While not true unit tests that test each function or method of a given module or class, basic unit tests help with testing overall module workflows.

Unit tests reside in the "./tests" directory and start with "test__".

## Running the tests
To run all the unit tests do <sup>[1]</sup>: `py -3 -m unittest` from within the "./tests" directory. 

## Using the command line
All of the unit tests have command line options.

To see the options and usage examples simply call the scripts with the `-h` option: `py -3 test__[rest of filename].py -h` and try the example.

Sample files are located in the "./tests/sample_files" directory.

The sample files can be used with the command line options of some of the unit tests.

# Modules
TOMES Packager consists of single-purpose high, level module, **packager.py**. This creates a TOMES archival information package (AIP). It can be used as native Python class or as command line script.

## Using packager.py with Python
To get started, import the module and run help():

	>>> from tomes_packager import packager
	>>> help(packager)

*Note: docstring and command line examples may reference sample and data files that are NOT included in the installed Python package. Please use appropriate paths to sample and data files as needed.*

## Using packager.py from the command line
1. From the "./tomes\_packager" directory do: `py -3 packager.py -h` to see an example command.
2. Run the example command.

-----
*[1] Depending on your system configuration, you might need to specify "python3", etc. instead of "py -3" from the command line. Similar differences might apply for PIP.*

