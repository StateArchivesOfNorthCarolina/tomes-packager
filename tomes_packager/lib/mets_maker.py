""" This module contains a class for constructing a METS document from a given METS template 
file. """

# import modules.
import jinja2
import logging
import logging.config
import os
from datetime import datetime
from lxml import etree

    
class METSMaker():
    """ A class for constructing a METS document from a given METS template file.
    
        Attributes:
            - mets (str): The rendered METS. If the template hasn't been successfully 
            rendered, this will be None.
            - mets_el (lxml.etree._Elment): The rendered METS. If the template hasn't been 
            successfully rendered, this will be None.

        Example:
            >>> mm = METSMaker("../../mets_templates/test.xml",
            >>>                 timestamp = lambda: datetime.now().isoformat() + "Z",
            >>>                 folders = [])
            >>> mm.make()
            >>> mm.validate()
            >>> print(mm.mets)
    """


    def __init__(self, mets_template="", charset="utf-8", evaluate=True, *args, **kwargs):
        """ Sets instance attributes.
        
        Args:
            - mets_template (str): The file path for the METS template file using Jinja
            templates. Note that the Jinja template start AND stopping strings are set to "%%"
            instead of the defaults. Also, XML comments beginning and ending with "<!--#" and
            "#-->" will not be outputted and may be used as in-line template documentation.
            - charset (str): The encoding for the rendered METS document.
            - evaluate (bool): If True, a time-stamped validation comment will be appended to
            the rendered METS document.
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
        self.charset = charset
        self.evaluate = evaluate
        self.args = args
        self.kwargs = kwargs

        # set attributes for imported data.
        self.xsd = self._join_paths(os.path.dirname(__file__),  "mets_1-11.xsd")
        self.beautifier = self._join_paths(os.path.dirname(__file__),  
                "beautifier.xsl")

        # set results containers.
        self.mets = None
        self.mets_el = None


    def _beautify_mets(self, mets_el):
        """ Beautifies @mets XML with @self.beautifier.
        
        Args:
            - mets (lxml.etree._Element): The METS XML to beautify.
            
        Returns:
            lxml.etree._Element: The return value.
        """
      
        self.logger.info("Beautifying METS XML.")
      
        # load XSL beautifier.
        beautifier = etree.parse(self.beautifier)
      
        # beautify @mets.
        transformer = etree.XSLT(beautifier)
        mets = transformer(mets_el)
        
        return mets
    

    def validate(self, mets_el=None):
        """ Validates @mets_el against @self.xsd.

        Args:
            - mets (lxml.etree._Element): The METS XML to validate. If None, @self.mets_el
            will be used.

        Returns:
            bool: The return value. True for valid, otherwise False.
            If validation could not be performed because there is no Internet connection, None
            is returned.
        """

        self.logger.info("Validating METS.")
        
        # if needed, use @self.mets_el.
        if mets_el is None:
            mets_el = self.mets_el

        # start with premis that validation hasn't occurred.
        is_valid = None
        
        # load XSD.
        xsd = etree.parse(self.xsd)
        
        # create validator or return if no Internet connection exists.
        try:
            validator = etree.XMLSchema(xsd)
        except etree.XMLSchemaParseError as err:
            self.logger.warning("Unable to validate XML; likely no Internet connection.")
            self.logger.error(err)
            return is_valid
        
        # validate @mets.
        try:
            validator.assertValid(mets_el)
            self.logger.info("METS is valid.")            
            is_valid = True
        except etree.DocumentInvalid as err:
            self.logger.warning("METS is invalid.")
            self.logger.error(err)
            is_valid = False

        return is_valid


    def make(self):
        """ Renders @self.mets_template via Jinja to return a METS XML document.
            
        Returns:
            str: The return value.
            The METS document as a string.
            If the METS template has invalid XML or template syntax, None is returned.
        """

        self.logger.info("Rendering template: {}".format(self.mets_template))

        # open @self.mets_template.
        with open(self.mets_template, encoding=self.charset) as tf:
                mets = tf.read()
               
        # create the Jinja renderer.
        try:
            template = jinja2.Template(mets, trim_blocks=True, lstrip_blocks=True, 
                    block_start_string="%%", block_end_string="%%", 
                    comment_start_string="<!--#", comment_end_string="#-->")
        except jinja2.exceptions.TemplateSyntaxError as err:
            self.logger.warning("Can't render METS; template syntax is invalid.")
            self.logger.exception(err, exc_info=True)
            return None
        
        # render @self.mets_template.
        try:
            mets = template.render(*self.args, **self.kwargs)
        except (AttributeError, TypeError, jinja2.exceptions.UndefinedError) as err:
            msg = "Can't render METS; "
            msg += "check template for undefined variables or calls to non-functions."
            self.logger.warning(msg)
            self.logger.exception(err, exc_info=True)
            return None
        
        # convert @mets to an lxml.etree._Element.
        try:
            mets_el = etree.fromstring(mets)
        except etree.XMLSyntaxError as err:
            self.logger.warning("XML syntax error in template; can't render METS.")
            self.logger.error(err)
            return None

        # if @self.evaluate is True, add validation status as an XML comment.
        if self.evaluate:

            # validate @mets_el.
            is_valid = self.validate(mets_el)
            
            # make timestamp function.
            now = lambda: datetime.now().isoformat() + "Z"
            
            # determine validation status.
            if is_valid is None:
                msg = "WARNING: METS document could not be validated as of {}.".format(now())
            if not is_valid:
                msg = "CRITICAL: this METS document is invalid as of {}.".format(now())
            else:
                msg = "NOTE: this METS document is valid as of {}.".format(now())
            
            # update @mets_el with validation status.
            self.logger.info("Appending XML comment: {}".format(msg))
            mets_el.append(etree.Comment(msg))
        
        # beautify @mets_el and set @self.mets_el.
        mets_el = self._beautify_mets(mets_el)
        self.mets_el = mets_el
        
        # finalize @mets.
        mets = etree.tostring(mets_el, pretty_print=True, encoding=self.charset).decode(
                self.charset)
        self.mets = mets

        return mets


if __name__ == "__main__":
    pass