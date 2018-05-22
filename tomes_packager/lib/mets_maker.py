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
    """ A class for constructing a METS document from a given METS template file.

        Attribuutes:
            - is_valid (bool): Stored validation value if "evaluate" was set to True. 
            Otherwise, this is None.

        Example:
            >>> from datetime import datetime
            >>> mm = METSMaker("../../tests/sample_files/sample_mets_template.xml", "foo.xml",
            >>>     TIMESTAMP = lambda: datetime.now().isoformat() + "Z")
            >>> mm.make() # writes "foo.xml" METS file.
            >>> mm.validate() # True.
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
            - evaluate (bool): If True, a time-stamped validation comment will be appended to
            the METS file and it will be beautified. Use False if the METS file output is
            excepted to be large.
            - charset (str): The encoding for the rendered METS document.
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

        # set validation attribute.
        self.is_valid = None


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


    def _evaluate_mets(self, mets_el):
        """ Appends a validation statement to @mets_el.

        Args:
            - mets_el (lxml.etree._Element): The METS XML to beautify.
            
        Returns:
            lxml.etree._Element: The return value.
        """

        is_valid = self.is_valid
        
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

        return mets_el
    

    def validate(self):
        """ Validates @self.filepath against @self.xsd.

        Returns:
            bool: The return value. True for valid, otherwise False.
            None is returned if there is no Internet connection or @self.filepath is not a 
            file or has invalid XML syntax.
        """

        # if no METS is created, return None.
        if not os.path.isfile(self.filepath):
            self.logger.warning("Nothing to validate; trying using .make() first.")
            return is_valid
        
        self.logger.info("Validating METS file: {}".format(self.filepath))
        
        # start with premis that validation hasn't occurred.
        is_valid = None
         
        # create validator.
        try:
            xsd = etree.parse(self.xsd)        
            validator = etree.XMLSchema(xsd)
        except etree.XMLSchemaParseError as err:
            self.logger.warning("Can't parse '{}'; likely no Internet connection.".format(
                self.xsd))
            self.logger.error(err)
            return is_valid
        
        # load @self.filepath.
        try:
            with open(self.filepath, encoding=self.charset) as fp:
                mets_el = etree.fromstring(fp.read())
        except etree.XMLSyntaxError as err:
            self.logger.warning("Can't validate malformed '{}'; check template syntax.")
            self.logger.error(err)
            return is_valid

        # validate @mets_el.
        try:
            validator.assertValid(mets_el)
            self.logger.info("METS is valid.")            
            is_valid = True
        except etree.DocumentInvalid as err:
            self.logger.warning("METS is invalid.")
            self.logger.error(err)
            is_valid = False

        # set @self._is_valid.
        self.is_valid = is_valid

        # if @self.evaluate is True; append a validation statement to the METS.
        if self.evaluate:
            
            # evaluate and beautify the METS.
            mets_el = self._evaluate_mets(mets_el)            
            mets_el = self._beautify_mets(mets_el)
    
            # rewrite @self.filepath with the updated METS.
            with open(self.filepath, "w", encoding=self.charset) as xf:
                mets = etree.tostring(mets_el, pretty_print=True, encoding=self.charset)
                mets = mets.decode(self.charset)
                xf.write(mets)

            # prevent further evaluation.
            self.evaluate = False

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
        try:
            template = jinja2.Template(mets_template, trim_blocks=True, lstrip_blocks=True, 
                    block_start_string="%%", block_end_string="%%", 
                    comment_start_string="<!--#", comment_end_string="#-->")
        except jinja2.exceptions.TemplateSyntaxError as err:
            self.logger.warning("METS template syntax is invalid.")
            self.logger.exception(err, exc_info=True)
            return
        
        # render @self.mets_template; write results to @self.filepath.
        try:
            mets = template.stream(*self.args, **self.kwargs)
            with open(self.filepath, "w") as f:
                i = 0
                for line in mets:
                    f.write(line)
                    i += 1
                    if (i % 100) == 0:
                        self.logger.info("Lines written: {}".format(i))
                self.logger.info("Created METS file: {}".format(self.filepath))
        except (AttributeError, TypeError, jinja2.exceptions.UndefinedError) as err:
            msg = "Can't render METS; "
            msg += "check template for undefined variables or calls to non-functions."
            self.logger.warning(msg)
            self.logger.exception(err, exc_info=True)
            return
        
        # if needed, validate METS.
        if self.evaluate:
            self.validate()

        return self.filepath


if __name__ == "__main__":
    pass

"""
    So just create another instance of METS MAKER in packager.
    And set evalute to False.
    Don't validate the manifest due to size.

    Finally, have a streaming=TRUE option OR just always stream the output.
    And log every nth write to file.
    Issue there is you don't want move the METS into the AIP until the METS is rendered.
    Otherwise, the METS file itself will show.

        # ??? MOVE TO METS MAKER AND HAVE THE TEMPLATE AS A LIB FILE? ???
        try:
            template = jinja2.Template(open(self.mets_manifest_template).read(), trim_blocks=True, lstrip_blocks=True, 
                    block_start_string="%%", block_end_string="%%", 
                    comment_start_string="<!--#", comment_end_string="#-->")
        except jinja2.exceptions.TemplateSyntaxError as err:
            self.logger.warning("Can't render METS; template syntax is invalid.")
            self.logger.exception(err, exc_info=True)
            return
        template.stream(**kwargs).dump(mets_path.replace(".xml", ".manifest"), encoding=self.charset)
"""
