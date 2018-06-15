# Introduction
**TOMES Packager** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to create a TOMES Archival Information Package (AIP) with the following structure:

    [account_id]/                        
    |  eaxs/                             
    |  |  attachments/*.*             # EAXS-encoded attachments
    |  |  xml/                 
    |  |  |  [account_id].xml         # EAXS version of the account.
    |  |  |  [account_id]_tagged.xml  # 'Tagged' version of EAXS.
    |  metadata/*.*                   # Optional data or administrative documents about the account (release forms, etc.)
    |  mime/*.*                       # EML or MBOX version of the account.
    |  pst/                
    |  |  [account_id].pst            # PST version of account (not required if account was exported as EML/MBOX).
    |  [account_id].mets.manifest     # Optional AIP manifest. Created by TOMES Packager. 
    |  [account_id].mets.xml          # Optional METS file with descriptive and/or preservation metadata. Created by TOMES Packager. 

In order to create the TOMES AIP, TOMES Packager requires the source data to be located in a *hot-folder*  that contains account files for one or more email accounts.

A hot-folder can have any root folder provided that the folder name does not contain whitespace.

The internal structure of the hot-folder must be as follows:

    {root}/
    |  eaxs/                          # Each account subfolder contains any and all EAXS files for the account.
    |  |  {account_id_01}/*.*
    |  |  {account_id_02}/*.*
    |  metadata/                      # Each account subfolder contains any and all optional data files for the account.
    |  |  {account_id_01}/*.*
    |  |  {account_id_02}/*.*
    |  mime/                          # Each account subfolder contains any and all EML or MBOX files for the accout.
    |  |  {account_id_01}/*.*
    |  |  {account_id_02}/*.*
    |  pst/                           # Contains a single, optional PST file for each account.
    |  |  {account_id_01}.pst
    |  {account_id_02}.pdf            # "Stray" account files are supported if the filename prefix exactly matches the AIP account_id.
    |  {account_id_02}.xlsx           # Stray files are NOT RECOMMENDED. Use the "metadata" folder instead.

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
TOMES Packager consists of single-purpose high, level module, **packager.py**. It can be used as native Python class or as command line script.

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

