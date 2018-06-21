# METS templates
Working with TOMES METS templates requires a high level of comfort not only with METS/XML, but also Python and the TOMES Packager Python module itself.

If you want to modify the included templates or create new ones, it is highly recommended that you study the included templates in depth.

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

A quick glance at this information shows that an understanding of `SELF` also requires an understanding of the modules in the "./tomes\_packager/lib" directory. In other words, some of the attributes of `SELF` are themselves instances of objects created by sub-modules.

Each sub-module has its own docstring and list of arguments and attributes. Review of the sub-module docstrings followed by further study of the included templates is recommended.

## Preservation Metadata
In addition to RDF/Dublin Core metadata that can be consumed via a .xlsx file, the command line and Python interfaces to TOMES Packager also allow for preservation data to be consumed and passed into a METS templates via a PREMIS log file.

A PREMIS log file is a plain-text file containing agent, event, and object metadata.

*For more information, see "./tomes\_packager/lib/premis\_object". For an example, see "./tests/sample\_files/sample_events.log".*

???TODO???: Work on this. This is a separate section and ask them to rerun it without the log param so they can see the difference. Adjust the docstring samples to that no PREMIS is created the first time. Also move the RDF stuff here. Finally, only put RDF and PREMIS example commands in this doc and leave them out of the main doc.

Using the Python interface, create an AIP with sample PREMIS and RDF/Dublin Core metadata:
	
	>>> from tomes_packager import packager
	>>> help(packager.Packager)

Now run the first example from the docstring or pass in the equivalent parameters to the command line interface. Finally, inspect the ".mets.xml" in the created AIP.
