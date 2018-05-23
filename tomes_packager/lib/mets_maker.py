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
            >>> mm = METSMaker("../../tests/sample_files/sample_mets_template.xml", "foo.xml",
            >>>     TIMESTAMP = lambda: datetime.now().isoformat() + "Z")
            >>> isfile(mm.filepath) # False            
            >>> mm.make() # writes "foo.xml" METS file.
            >>> mm.validate() # True
            >>> isfile(mm.filepath) # True
    """


    def __init__(self, mets_template, filepath, evaluate=True, charset="utf-8", *args,  
            **kwargs):
        """ Sets instance attributes.
        
        Args:
            - mets_template (str): The file path for the METS template file using Jinja
            templates. Note that the Jinja template start AND stopping strings are set to "%%"
            instead of the defaults. Also, XML comments beginning and ending with "<!--#" and
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

        # verify @path is a file.
        if not os.path.isfile(mets_template):
            msg = "Can't find: {}".format(mets_template)
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        # convenience functions to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")
        self._join_paths = lambda *p: self._normalize_path(os.path.join(*p))

        # set attributes.            
        self.mets_template = mets_template
        self.filepath = filepath
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
      
        # beautify @mets_el.
        beautifier = etree.parse(self._beautifier)
        transform = etree.XSLT(beautifier)
        mets_el = transform(mets_el)
        
        return mets_el


    def _evaluate_mets(self, mets_el, is_valid):
        """ Appends a validation statement to @mets_el.

        Args:
            - mets_el (lxml.etree._Element): The METS XML to beautify.
            - is_valid (bool): True if the METS file is valid. Otherwise, False.
            
        Returns:
            lxml.etree._Element: The return value.
        """
 
        # make timestamp function.
        now = lambda: datetime.now().isoformat() + "Z"
        
        # determine validation status.
        if is_valid is None:
            msg = "WARNING: METS file could not be validated as of {}.".format(now())
        if not is_valid:
            msg = "CRITICAL: this METS file is invalid as of {}.".format(now())
        else:
            msg = "NOTE: this METS file is valid as of {}.".format(now())
 
        # update @mets_el with validation status.
        self.logger.info("Appending XML comment: {}".format(msg))
        mets_el.append(etree.Comment(msg))

        return mets_el
    

    def validate(self):
        """ Validates @self.filepath against @self.xsd. In addition, a validation comment is
        appended to the METS file. The METS file is also beautified. DO NOT use this method 
        on very large METS files.

        Returns:
            bool: The return value. True for valid, otherwise False.
            None is returned if there is no Internet connection or @self.filepath is not a 
            file or has invalid XML syntax.
        """
        
        self.logger.info("Validating METS file: {}".format(self.filepath))

        # if no METS is created, return None.
        if not os.path.isfile(self.filepath):
            self.logger.warning("Nothing to validate; trying using .make() first.")
            return

        # create validator.
        try:
            xsd = etree.parse(self.xsd)        
            validator = etree.XMLSchema(xsd)
        except etree.XMLSchemaParseError as err:
            self.logger.warning("Can't parse '{}'; likely no Internet connection.".format(
                self.xsd))
            self.logger.error(err)
            return
        
        # load @self.filepath.
        try:
            with open(self.filepath, encoding=self.charset) as fp:
                mets_el = etree.fromstring(fp.read())
        except etree.XMLSyntaxError as err:
            self.logger.warning("Can't validate malformed '{}'; check template syntax.")
            self.logger.error(err)
            return

        # validate @mets_el.
        try:
            validator.assertValid(mets_el)
            self.logger.info("METS is valid.")            
            is_valid = True
        except etree.DocumentInvalid as err:
            self.logger.warning("METS is invalid.")
            self.logger.error(err)
            is_valid = False

        # add validation statement to METS and beautify it.
        mets_el = self._evaluate_mets(mets_el, is_valid)            
        mets_el = self._beautify_mets(mets_el)
        mets = etree.tostring(mets_el, pretty_print=True, encoding=self.charset)
        mets = mets.decode(self.charset)    
        
        # rewrite @self.filepath with the updated METS.
        with open(self.filepath, "w", encoding=self.charset) as xf:
            xf.write(mets)

        return is_valid


    def make(self):
        """ Renders @self.mets_template via Jinja to return a METS XML document.
            
        Returns:
            str: The return value.
            The METS filepath.
            If the METS can't be created, None is returned.
        """

        self.logger.info("Rendering template: {}".format(self.mets_template))

        # open @self.mets_template.
        with open(self.mets_template, encoding=self.charset) as tf:
                mets_template = tf.read()
               
        # create the Jinja renderer.
        # Note: without "exc_info=False" tracebacks seem to be going into logs.
        try:
            template = jinja2.Template(mets_template, trim_blocks=True, lstrip_blocks=True, 
                    block_start_string="%%", block_end_string="%%", 
                    comment_start_string="<!--#", comment_end_string="#-->")
        except jinja2.exceptions.TemplateSyntaxError as err:
            self.logger.warning("METS template syntax is invalid.")
            self.logger.exception(err, exc_info=False)
            raise
        
        # render @self.mets_template; write results to @self.filepath.
        self.logger.info("Creating METS file: {}".format(self.filepath))        
        try:
            mets = template.stream(*self.args, **self.kwargs)
            with open(self.filepath, "w") as f:
                i = 0
                for line in mets:
                    f.write(line)
                    if (i + 1 % 1) == 0:
                        self.logger.debug("METS lines written: {}".format(i))
                    i += 1
        except (AttributeError, TypeError, jinja2.exceptions.UndefinedError) as err:
            msg = "Can't fully render METS file."
            msg += "; check template for undefined variables or calls to non-functions."
            msg += "; partially rendered files will be invalid."
            self.logger.warning(msg)
            self.logger.exception(err, exc_info=False)
            raise

        return self.filepath


if __name__ == "__main__":
    pass
