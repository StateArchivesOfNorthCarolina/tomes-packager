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

The `./tomes_packager/packager.py` module's docstring contains a list of object arguments and available attributes.

A quick glance at this information shows that an understanding of `SELF` also requires an understanding of the modules in the module's "lib" directory. In other words, some of the attributes of `SELF` are themselves instances of objects created by library sub-modules. Each sub-module has its own docstring and list of arguments and attributes.

Review of the docstrings followed by further study of the included templates is recommended.

### Preservation and Descriptive Metadata
#### PREMIS compatible data
... `SELF.premis_obj`

#### RDF/Dublin Core metadata
... `SELF.rdf_obj`

Excel rules ???