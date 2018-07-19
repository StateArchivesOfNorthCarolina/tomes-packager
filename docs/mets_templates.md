# METS templates
Working with TOMES METS Templates requires a high level of comfort not only with METS/XML, but also Python and the TOMES Packager Python module itself.

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

*Note: Do not add XML declarations (`<?xml version="1.0"?>`, etc.) to templates.*

### @SELF
The `SELF` variable used in the included templates equates to the current instance of the `tomes_packager.packager.Packager` Python object.

The `./tomes_packager/packager.py` module's docstring contains a list of object arguments and available attributes.

A quick glance at this information shows that an understanding of `SELF` also requires an understanding of the modules in the `./tomes_packager/lib` directory. In other words, some of the attributes of `SELF` are themselves instances of objects created by sub-modules.

Each sub-module has its own docstring and list of arguments and attributes. Review of the sub-module docstrings followed by further study of the included templates is recommended.