""" This module contains a class for constructing a TOMES archival information package (AIP)
with an optional METS file.

Todo:
    * Verify template is a file on __init__.
        - And verify base is a folder.
    * Need to determine constant vars.
        - ISO/UTC now (aka @timstamp).
        - What else?
    * Need to catch validation attempts run without an internet connection.
"""


# import modules.
import jinja2
import logging
import logging.config
import os
from datetime import datetime
from lxml import etree
from lib.aip_maker import AIPMaker
from lib.directory_object import DirectoryObject
from lib.events_object import EventsObject

    
class Packager():
    """ A class for constructing a TOMES archival information package (AIP) with an optional 
    METS file. """


    def __init__(self, account_id, source_dir, destination_dir, mets_template="", 
            preservation_events={}, charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            - account_id (str): The email account's base identifier, i.e. the file prefix.
            - source_dir (str): The folder path from which to transfer data.
            - destination_dir (str): The folder path in which to create the AIP structure.
            - mets_template (str): The file path for the METS template. This will be used to
            render a METS file inside the AIP's root folder. For more information, see: 
            "https://github.com/StateArchivesOfNorthCarolina/tomes-packager/blob/master/docs/documentation.md".
            - preservation_events (dict): Optional preservation events to pass into 
            @mets_template.
            - charset (str): The encoding for the rendered METS file.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience functions to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")
        self._abspath = lambda p: self._normalize_path(os.path.abspath(p))

        # set attributes.
        self.account_id = str(account_id) 
        self.source_dir = self._normalize_path(source_dir)
        self.destination_dir = self._normalize_path(destination_dir)
        self.preservation_events = EventsObject(preservation_events)
        self.mets_template = mets_template
        self.charset = charset

        # set attributes for imported modules and data.
        self._aip_maker = AIPMaker
        self._directory_object = DirectoryObject
        self._mets_xsd = self._normalize_path(os.path.dirname(os.path.abspath(__file__)) + 
                "/lib/mets_1-11.xsd")
        self._xml_beautifier = self._normalize_path(os.path.dirname(\
                os.path.abspath(__file__)) + "/lib/beautifier.xsl")


    def _beautify_mets(self, mets):
        """ Beautifies @mets XML with @self.xml_beautifier.
        
        Args:
            - mets (lxml.etree._Element): The METS XML to beautify.
            
        Returns:
            lxml.etree._Element: The return value.
        """
      
        self.logger.info("Beautifying METS XML.")
      
        # load XSL beautifier.
        beautifier = etree.parse(self._xml_beautifier)
      
        # beautify @mets.
        transformer = etree.XSLT(beautifier)
        mets = transformer(mets)
        
        return mets
    

    def _validate_mets(self, mets):
        """ Validates @mets XML against @self.xsd.
        
        Args:
            - mets (lxml.etree._Element): The METS XML to validate.
            
        Returns:
            bool: The return value. True for valid, otherwise False.
        """

        self.logger.info("Validating METS XML.")
        
        # load XSD.
        xsd = etree.parse(self._mets_xsd)
        validator = etree.XMLSchema(xsd)
        
        # validate @mets.
        try:
            validator.assertValid(mets)
            self.logger.info("METS XML is valid.")            
            is_valid = True
        except etree.DocumentInvalid as err:
            self.logger.warning("METS XML is invalid.")
            self.logger.error(err)
            is_valid = False

        return is_valid


    def _render_mets(self, *args, **kwargs):
        """ Renders @self.mets_template via Jinja to return a METS XML document. Note that the
        Jinja template start AND stopping strings are set to "%%" instead of the defaults. 
        Also, XML comments beginning and ending with "<!--#" and "#-->" will not be outputted
        and may be used as in-line template documentation.
        
        Args:
            - *args/**kwargs: The optional arguments to pass to the Jinja formatter.
            
        Returns:
            lxml.etree._Element: The return value.
            If the template has invalid XML syntax, None is returned.

        Raises:
            - jinja2.exceptions.UndefinedError: If @self.mets_template can't be rendered.
        """

        self.logger.info("Rendering template: {}".format(self.mets_template))

        # open @self.mets_template.
        with open(self.mets_template, encoding=self.charset) as tf:
                mets = tf.read()
               
        # create the Jinja renderer.
        template = jinja2.Template(mets, trim_blocks=True, lstrip_blocks=True, 
                block_start_string="%%", block_end_string="%%", comment_start_string="<!--#",
                comment_end_string="#-->")
        
        # render @self.mets_template.
        try:
            mets = template.render(*args, **kwargs)
        except jinja2.exceptions.UndefinedError as err:
            self.logger.warning("Unable to render template; skipping METS creation.")
            self.logger.error(err)
            return None
        
        # convert @mets to an lxml.etree._Element.
        try:
            mets = etree.fromstring(mets) 
        except etree.XMLSyntaxError as err:
            self.logger.warning("XML syntax error in template; skipping METS creation.")
            self.logger.error(err)
            return None

        return mets


    def package(self):
        """ Creates the AIP structure and optional METS file.
        
        Returns:
            tuple: The return value.
            The first item is he AIP folder's absolute path. The second item is the METS 
            file's base name (None if no METS was created). The third item is a boolean:
            False if the AIP structure and/or the METS is invalid and/or the METS template
            failed to render (likely due to user error). Otherwise, True.
        """

        # create function to get ISO timestamp. 
        timestamp = lambda: datetime.utcnow().isoformat() + "Z"

        # set AIP path.
        aip_dir = self._abspath(os.path.join(self.destination_dir, 
            self.account_id))
        self.logger.info("Packaging: {}".format(aip_dir))

        # create AIP structure.
        aip = self._aip_maker(self.account_id, self.source_dir, self.destination_dir)
        aip.make()

        # if the AIP structure isn't valid, warn but continue on.
        if not aip.validate():
            self.logger.warning("AIP structure is invalid; continuing anyway.")

        # if no METS template was passed; return AIP.
        if self.mets_template == "":
            self.logger.info("No METS template passed; skipping METS creation.")
            return (aip_dir, None, aip.validate())

        # otherwise, create a DirectoryObject for the AIP.
        aip_obj = self._directory_object(aip_dir)

        # create METS from @self.mets_template.
        mets = self._render_mets(timestamp = timestamp, 
                folders = aip_obj.dirs, 
                files = aip_obj.files,
                graph = "\n" + aip_obj.rdirs.ls(),
                events = self.preservation_events)
        
        # is the METS template failed to render, return AIP and mark it invalid.
        if mets is None:
            return (aip_dir, None, False)
        
        # validate @mets and add validation status as an XML comment.
        is_mets_valid = self._validate_mets(mets)
        if is_mets_valid:
            msg = "NOTE: this METS document is valid as of {}.".format(timestamp())
        else:
            msg = "WARNING: this METS document is valid as of {}.".format(timestamp())
        mets.append(etree.Comment(msg))
       
        # beautify @mets.
        mets = self._beautify_mets(mets)

        # convert @mets to a string.
        mets = etree.tostring(mets, pretty_print=True, encoding=self.charset).decode(
                self.charset)
        
        # set the METS file path.
        mets_file = "{}.mets.xml".format(self.account_id)
        mets_path = os.path.join(self._abspath(self.destination_dir), self.account_id,
                mets_file)
        mets_path = self._abspath(mets_path)
        
        # write @mets to file.
        with open(mets_path, "w", encoding=self.charset) as mf:
            mf.write(mets)
            
        # determine if both the AIP and the METS are valid.
        aip_validity = bool(aip.validate() * is_mets_valid)

        return (aip_dir, mets_file, aip_validity)


# TEST.
if __name__ == "__main__":

    logging.basicConfig(level="DEBUG")

    p = Packager("foo", 
            "../tests/sample_files/hot_folder", 
            "../tests/sample_files", 
            "../mets_templates/test.xml",
            {"20180101":["fooevent", None]})
    
    aip = p.package()
    print(aip)
    pass
