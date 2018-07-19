# Introduction

**TOMES Packager** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to create a TOMES Archival Information Package (AIP) with an optional [METS](https://www.loc.gov/standards/mets/) file and an optional METS manifest file.

## AIP Structure and Content
A TOMES AIP has the following structure:

    [account_id]/                        
    |  eaxs/                             
    |  |  attachments/*.*             # EAXS-encoded attachments
    |  |  xml/                 
    |  |  |  [account_id].xml         # EAXS version of the account.
    |  |  |  [account_id]_tagged.xml  # "Tagged" version of EAXS.
    |  metadata/*.*                   # Optional data or administrative documents about the account (release forms, etc.)
    |  mime/*.*                       # EML or MBOX version of the account.
    |  pst/                
    |  |  [account_id].pst            # PST version of account (not required if account was exported as EML/MBOX).
    |  [account_id].mets.manifest     # Optional AIP manifest. Created by TOMES Packager. 
    |  [account_id].mets.xml          # Optional METS file with descriptive and/or preservation metadata. Created by TOMES Packager. 

In order to create a TOMES AIP, TOMES Packager requires the source data to be located in a *hot-folder*  that contains account files for one or more email accounts.

### Hot Folders

A hot-folder can have any root folder provided that the folder name does not contain whitespace. Likewise, account identifiers must not contain whitespace.

The internal structure of the hot-folder must be as follows:

    [root]/
    |  eaxs/                          # Each account subfolder contains any and all EAXS files and folders for the account.
    |  |  [account_id_01]/*.*
    |  |  [account_id_02]/*.*
    |  metadata/                      # Each account subfolder contains any and all optional data files and folders for the account.
    |  |  [account_id_01]/*.*
    |  |  [account_id_02]/*.*
    |  mime/                          # Each account subfolder contains any and all EML or MBOX files and folders for the account.
    |  |  [account_id_01]/*.*
    |  |  [account_id_02]/*.*
    |  pst/                           # Contains a single, optional PST file for each account.
    |  |  [account_id_01].pst
    |  [account_id_02].pdf            # "Stray" account files are supported if the filename prefix exactly matches the AIP account_id.
    |  [account_id_02].xlsx           # Stray files are NOT RECOMMENDED. Use the "metadata" folder instead.

### METS Files
TOMES Packager supports the creation of two types of METS files:

 1. A METS file for descriptive, rights, and preservation metadata.
 2. A METS manifest file to store information about all files within the final AIP.

The justification for two METS files is that large AIP folders containing many files (e.g. EML and attachment files) can easily render a METS file too large to manually inspect, edit, or even open in GUI text and XML editors.

TOMES Packager uses *TOMES METS Templates* in order to receive information on how to construct a given METS or METS manifest file.

#### Included METS templates
Due to the complexity of creating templates, the following template files are included with TOMES Packager:
 
 1. `./tomes_packager/mets_templates/default.xml`
	* The default template for METS files with support for descriptive and preservation metadata. *See the sections below on adding descriptive and preservation metadata.*
 2. `./tomes_packager/mets_templates/basic.xml`
	* Supports descriptive metadata only.
 3. `./tomes_packager/mets_templates/nc_gov.xml`
 	* Created according to the State of North Carolina's requirements.
 4. `./tomes_packager/mets_templates/MANIFEST.XML`
 	* The default template for METS manifest files.

*For more detailed information on TOMES METS Templates, see the `mets_templates.md` file located in the same directory as this documentation file.*

#### Adding Descriptive Metadata to METS
The included METS templates support ingest of Dublin Core metadata from a single ".xlsx" file. The Dublin Core will be wrapped as RDF/XML.

The ".xlsx" file must be passed as a parameter to TOMES Packager via Python or the command line interface.

*For more information, see `./tests/sample_files/sample_rdf.xlsx`.*

#### Adding Preservation Metadata to METS
Preservation data can be consumed and passed into supporting METS templates via a PREMIS log file.

A PREMIS log file is a plain-text file containing agent, event, and object metadata.

The general idea behind the PREMIS log file is that it will be a concatenation of one-to-many special logging files outputted by various software components of the TOMES project. In other words, these components will output PREMIS compatible log files containing information about themselves (agents), the actions they performed (events), and the data acted upon or created as a result of such actions (objects).

Each log line is a YAML string with an ISO timestamp as the key. Its value is a set of key/value pairs with the required keys "name" and "entity".

Per the docstring for `./tomes_packager/lib/premis_object.py`:

> The value for "name" can be any token, although whitespace is not technically banned. The only value options for "entity" are: "agent", "event", or "object". Additional attributes may also exist. Note that the attribute "timestamp" is reserved as it is created automatically. Its value will be equal to the key itself, i.e. the ISO timestamp. 

Additionally, any keys referenced in a given METS template would also be required.

The log file must be passed as a parameter to TOMES Packager via Python or the command line interface.

*For an example log, see `./tests/sample_files/sample_premis.log`.*

# External Dependencies
TOMES Packager requires the following:

- [Python](https://www.python.org) 3.0+ (using 3.5+)
  - See the `./requirements.txt` file for additional module dependencies.
  - You will also want to install [pip](https://pypi.python.org/pypi/pip) for Python 3.

If you want to use TOMES Packager to create Dublin Core/METS metadata, you will also need Microsoft Office 2007+ or another suite, such as [LibreOffice](https://www.libreoffice.org), capable of creating Excel 2007+ Excel files (.xlsx).

# Installation
After installing the external dependencies above, you'll need to install some required Python packages.

The required packages are listed in the `./requirements.txt` file and can easily be installed via PIP <sup>[1]</sup>: `pip3 install -r requirements.txt`

You should now be able to use TOMES Packager from the command line or as a locally importable Python module.

If you want to install TOMES Packager as a Python package, do: `pip3 install . -r requirements.txt`

Running `pip3 uninstall tomes_packager` will uninstall the TOMES Packager package.

# Unit Tests
While not true unit tests that test each function or method of a given module or class, basic unit tests help with testing overall module workflows.

Unit tests reside in the `./tests` directory and start with "test__".

## Running the tests
To run all the unit tests do <sup>[1]</sup>: `py -3 -m unittest` from within the `./tests` directory. 

## Using the command line
All of the unit tests have command line options.

To see the options and usage examples simply call the scripts with the `-h` option: `py -3 test__[rest of filename].py -h` and try the example.

Sample files are located in the `./tests/sample_files` directory.

The sample files can be used with the command line options of some of the unit tests.

# Modules
TOMES Packager consists of single-purpose high, level module, `packager.py`. It can be used as native Python class or as command line script.

## Using packager.py with Python
To get started, import the module and run help():

	>>> from tomes_packager import packager
	>>> help(packager)

*Note: docstring and command line examples may reference sample and data files that are NOT included in the installed Python package. Please use appropriate paths to sample and data files as needed.*

## Using packager.py from the command line
1. From the `./tomes_packager` directory do: `py -3 packager.py -h` to see an example command.
2. Run the example command.
3. Inspect the created AIP at `./tests/sample_files/foo` and its METS files.
4. Run the example command with the following changes:
	* Change the `account_id` parameter value from `foo` to `bar`.
	* Append the following parameters:
		* `-premis-log="../tests/sample_files/sample_premis.log"`
		* `-rdf-xlsx="../tests/sample_files/sample_rdf.xlsx"`
5. Inspect the created AIP at `./tests/sample_files/bar`.
	* Compare the data in the METS file, `../tests/sample_files/bar.mets.xml`, to the source data in the RDF and PREMIS log files that were passed in.

*Note: You can reset the hot-folder by running `../tests/sample_files/reset_hot_folder.py`. This will delete the `foo` and `bar` AIP folders.*

-----
*[1] Depending on your system configuration, you might need to specify "python3", etc. instead of "py -3" from the command line. Similar differences might apply for PIP.*
