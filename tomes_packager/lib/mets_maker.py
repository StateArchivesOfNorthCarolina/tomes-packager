""" This module contains a class for constructing a METS file from a given METS template 
file. """

# import modules.
import jinja2
import logging
import logging.config
import os
from datetime import datetime
from lxml import etree

    
class METSMaker():
    """ A class for constructing a METS file from a given METS template file.

        Example:
            >>> from os.path import isfile
            >>> from datetime import datetime
            >>> mm = METSMaker("../../tests/sample_files/sample_mets_template.xml", 
                    "foo.xml",
                    TIMESTAMP = lambda: datetime.now().isoformat() + "Z")
            >>> isfile(mm.filepath) # False            
            >>> mm.make() # writes "foo.xml" METS file.
            >>> mm.validate() # True
            >>> isfile(mm.filepath) # True
    """


    def __init__(self, mets_template, filepath, evaluate=True, charset="utf-8", *args,  
            **kwargs):
        """ Sets instance attributes.
        
        Args:
            - mets_template (str): The file path for the Jinja METS template file. Note that 
            the Jinja template start AND stopping strings are set to "%%" instead of the 
            defaults. Also, XML comments beginning and ending with "<!--#" and
            "#-->" will not be outputted and may be used as in-line template documentation.
            - filepath (str): The file path to which to write the METS.
            - charset (str): The encoding for the rendered METS file.
            - *args/**kwargs: The optional arguments to pass into @mets_template.

        Raises:
            - FileNotFoundError: If @mets_template is not an actual file path.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # verify @mets_template is a file.
        if not os.path.isfile(mets_template):
            msg = "Can't find: {}".format(mets_template)
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        # convenience functions to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")
        self._join_paths = lambda *p: self._normalize_path(os.path.join(*p))

        # set attributes.            
        self.mets_template = self._normalize_path(mets_template)
        self.filepath = self._normalize_path(filepath)
        self.charset = charset
        self.evaluate = evaluate
        self.args = args
        self.kwargs = kwargs

        # set attributes for imported data.
        self.xsd = self._join_paths(os.path.dirname(__file__),  "mets_1-11.xsd")
        self._beautifier = self._join_paths(os.path.dirname(__file__),  
                "beautifier.xsl")


    def _beautify_mets(self, mets_el):
        """ Beautifies @mets_el XML with @self.beautifier.
        
        Args:
            - mets_el (lxml.etree._Element): The METS XML to beautify.
            
        Returns:
            lxml.etree._Element: The return value.
        """
      
        self.logger.info("Beautifying METS XML.")
      
        # load XSLT.
        beautifier = etree.parse(self._beautifier)
        
        # update XSLT's "encoding" attribute.
        beautifier.find("{http://www.w3.org/1999/XSL/Transform}output").set("encoding", 
                self.charset)
        
        # beautify @mets_el.
        transform = etree.XSLT(beautifier)
        mets_el = transform(mets_el)
        
        return mets_el


    def _evaluate_mets(self, mets_el, is_valid):
        """ Appends a validation statement to @mets_el.

        Args:
            - mets_el (lxml.etree._Element): The METS XML to which to append a validation
            statement.
            - is_valid (bool): True if the METS file is valid. Otherwise, False.
            
        Returns:
            lxml.etree._Element: The return value.
        """
 
        self.logger.info("Evaluating METS XML.")

        # make timestamp function.
        now = lambda: datetime.now().isoformat() + "Z"
        
        # determine validation status.
        if is_valid is None:
            msg = "WARNING: METS file could not be validated as of {}.".format(now())
        elif not is_valid:
            msg = "CRITICAL: this METS file is invalid as of {}.".format(now())
        else:
            msg = "NOTE: this METS file is valid as of {}.".format(now())
 
        # update @mets_el with validation status.
        self.logger.debug("Appending XML comment: {}".format(msg))
        mets_el.append(etree.Comment(msg))

        return mets_el
    

    def validate(self):
        """ Validates @self.filepath against @self.xsd. In addition, a validation comment is
        appended to the METS file. The METS file is also beautified. Note: this reads the METS
        file into memory and rewrites it. Files over 10 megabytes are disallowed and will
        automatically result in a return of False.

        Returns:
            bool: The return value. True if and only if the METS file could be validated and 
            is valid. Otherwise, False.
        """
        
        self.logger.info("Validating METS file: {}".format(self.filepath))

        # if no METS is created, return False.
        if not os.path.isfile(self.filepath):
            self.logger.warning("Nothing to validate; trying using .make() first.")
            return False

        # if the METS file is greater than 10 megabytes, return False.
        if os.stat(self.filepath).st_size > 10485760:
            self.logger.warning("METS file is too large to validate; returning False.")
            return False

        # create validator.
        try:
            xsd = etree.parse(self.xsd)        
            validator = etree.XMLSchema(xsd)
        except etree.XMLSchemaParseError as err:
            self.logger.warning("Can't parse '{}'; check Internet connection.".format(
                self.xsd))
            self.logger.error(err)
            validator = None        
        
        # load @self.filepath.
        try:
            with open(self.filepath, encoding=self.charset) as fp:
                mets_el = etree.fromstring(fp.read())
        except etree.XMLSyntaxError as err:
            self.logger.warning("Bad XML syntax in '{}'; check template.".format(
                self.filepath))
            self.logger.error(err)
            return False

        # validate @mets_el.
        is_valid = False
        if validator is not None:
            try:
                validator.assertValid(mets_el)
                self.logger.info("METS is valid.") 
                is_valid = True
            except etree.DocumentInvalid as err:
                self.logger.warning("METS is invalid.")
                self.logger.error(err)
        else:
            self.logger.warning("Unable to perform validation.")

        # add validation statement to METS; beautify XML.
        if validator is not None:
            mets_el = self._evaluate_mets(mets_el, is_valid)
        else:
            mets_el = self._evaluate_mets(mets_el, None)
        mets_el = self._beautify_mets(mets_el)
        mets = etree.tostring(mets_el, pretty_print=True, encoding=self.charset)
        mets = mets.decode(self.charset)
        
        # rewrite @self.filepath with the updated METS.
        with open(self.filepath, "w", encoding=self.charset) as xf:
            xf.write(mets)

        return is_valid


    def make(self):
        """ Renders @self.mets_template via Jinja and returns a METS XML document provided
        @self.filepath is not an existing file.
            
        Returns:
            None: The return value.

        Raises:
            - ValueError: If the Jinja template syntax is incorrect.
        """

        # verify @filepath doesn't already exist.
        if os.path.isfile(self.filepath):
            msg = "METS file '{}' already exists; it will not be overwritten.".format(
                    self.filepath)
            self.logger.info(msg)
            return
        else:
            self.logger.info("Rendering METS template: {}".format(self.mets_template))

        # open @self.mets_template.
        with open(self.mets_template, encoding=self.charset) as tf:
                mets_template = tf.read()
               
        # create the Jinja renderer.
        try:
            template = jinja2.Template(mets_template, trim_blocks=True, lstrip_blocks=True, 
                    block_start_string="%%", block_end_string="%%", 
                    comment_start_string="<!--#", comment_end_string="#-->")
        except jinja2.exceptions.TemplateSyntaxError as err:
            self.logger.warning("METS template syntax is invalid.")
            self.logger.error(err)
            raise ValueError(err)
        
        # render @self.mets_template as a stream; write results to @self.filepath.
        self.logger.info("Creating METS file: {}".format(self.filepath))        
        try:
            mets = template.stream(encoding=self.charset, *self.args, **self.kwargs)
            with open(self.filepath, "w", encoding=self.charset) as f:
                i = 0
                for line in mets:
                    line = line.encode(self.charset, errors="xmlcharrefreplace").decode(
                            self.charset)
                    f.write(line)
                    if (i + 1) % 100 == 0:
                        self.logger.debug("Current write operation: {}".format(i))
                    i += 1
        except (AttributeError, TypeError, jinja2.exceptions.UndefinedError) as err:
            msg = "Can't fully render METS file."
            msg += "; check template for undefined variables or calls to non-functions."
            msg += "; partially rendered files will be invalid."
            self.logger.warning(msg)
            self.logger.error(err)
            raise ValueError(err)

        return


if __name__ == "__main__":
    pass
