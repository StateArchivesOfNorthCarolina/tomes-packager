# Adding METS to packages
TOMES Packager supports the creation of two types of METS files:

 1. A METS file for descriptive, rights, and preservation metadata.
 2. A METS manifest file to store information about all files within the final TOMES Archival Information Package (AIP).

The justification for two METS files is that large AIP folders containing many files (EML and attachment files) can easily render a METS file too large to manually inspect, edit, or even open in GUI text and XML editors.

TOMES Packager uses *TOMES METS Templates* in order to receive information on how to construct a given METS or METS manifest file.

Working with the templates requires a high level of comfort not only with METS, but also Python and the TOMES Packager Python module itself.

## Included templates
Due to the complexity of creating the templates, three template files are included with TOMES Packager:
 
 1. **./tomes\_packager/mets\_templates/default.xml**
	* The default template for METS files.
 2. **./tomes\_packager/mets\_templates/nc_gov.xml**
 	* The default template for the State of North Carolina.
 3. **./tomes\_packager/mets\_templates/MANIFEST.XML**
 	* The default template for METS manifest files.

If you want to modify the existing templates or create new ones, it is highly recommended that you study these templates in depth.

## Understanding templates
METS templates use the [Jinja](http://jinja.pocoo.org) template syntax and are automatically fed an instance of the `tomes_packager.packager.Packager` Python object as the variable `SELF`.

### Jinja syntax
While Jinja templates are well-known to many Python developers, TOMES Packager makes the following modifications to the standard Jinja syntax:

 1. **Both** opening and closing block strings, `{%` and `%}`, are replaced by `%%`.
 2. XML comments with closing and opening hash marks will not appear in rendered templates and should be used for comments about the template. Normal XML comments will appear in the rendered templates and should be used for comments about the METS data itself. In other words:
   * `<!--# This will not appear in a rendered template. #-->`
   * `<!-- But this will. -->`
   * `<!-- # And so will this (because the hash marks aren't flush with the hyphens). # -->`

### @SELF
The `SELF` variable used in the included templates equates to the current instance of the `tomes_packager.packager.Packager` Python object.

The "./tomes_packager/packager.py" module's docstring contains a list of object arguments and available attributes.

A quick glance at this information shows that an understanding of `SELF` also requires an understanding of the modules in the "./tomes\_packager/lib" directory.In other words, some of the attributes of `SELF` are themselves instances of objects created by sub-modules.

Each sub-module has its own docstring and list of arguments and attributes. Review of the sub-module docstrings followed by further study of the included templates is recommended.

### Preservation and Descriptive Metadata
Both the command line and Python interface to TOMES Packager allow for two types of data files to be consumed and passed into the METS templates:

 1. A **PREMIS log**: A plain-text file containing agent, event, and object metadata.
	* For more information, see "./tomes\_packager/lib/premis\_object".
	* For an example, see "./tests/sample\_files/sample_events.log".
 2. An **RDF .xlsx file**: An Excel 2007+ file with Dublin Core metadata.
 	* For more information, see "./tomes\_packager/lib/rdf\_maker".
 	* For an example and information on how to create valid metadata worksheets, see "./tests/sample\_files/sample_rdf.xlsx".

Using the Python interface, create an AIP with sample PREMIS and RDF/Dublin Core metadata:
	
	>>> from tomes_packager import packager
	>>> help(packager.Packager)

Now run the first example from the docstring or pass in the equivalent parameters to the command line interface. Finally, inspect the ".mets.xml" in the created AIP.