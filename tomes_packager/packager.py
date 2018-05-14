""" ???

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
    """ ??? """

    def __init__(self, account_id, source_dir, destination_dir, preservation_events={}, 
            mets_template="", charset="utf-8"):
        """ ??? """

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
        """

        self.logger.info("Rendering template: {}".format(self.mets_template))

        # render @self.mets_template.
        with open(self.mets_template, encoding=self.charset) as tf:
                mets = tf.read()
                
        template = jinja2.Template(mets, trim_blocks=True, lstrip_blocks=True, 
                block_start_string="%%", block_end_string="%%", comment_start_string="<!--#",
                comment_end_string="#-->")
        
        try:
            mets = template.render(*args, **kwargs)
        except Exception as err:
            # TODO: What exceptions?
            self.logger.warning("Unable to render template.")
            self.logger.err(err)
            raise 
        
        # convert @mets to an lxml.etree._Element.
        mets = etree.fromstring(mets) 

        # validate @mets and add validation status as an XML comment.
        valid_msg = " It is {} that this METS is valid. ".format(self._validate_mets(mets))
        mets.append(etree.Comment(valid_msg))
        
        # beautify @mets.
        mets = self._beautify_mets(mets)
        
        return mets


    def package(self):
        """ ??? """

        self.logger.info("???")

        # ???
        try:
            aip = self._aip_maker(self.account_id, self.source_dir, self.destination_dir)
            aip.make()
        except Exception as err:
            self.logger.warning("???")
            self.logger.error(err)
            raise #TODO: raise what?

        # ???
        if not aip.validate():
            self.logger.warning("??? invalid AIP structure; trying anyway ...")
        if not self._abspath(self.destination_dir) == self._abspath(aip.destination_dir):
            self.logger.warning("???")


        # ???
        if self.mets_template == "":
            self.logger.info("???")
            return

        # ???
        try:
            aip_dir = self._normalize_path(os.path.join(self.destination_dir, 
                self.account_id))
            aip_obj = self._directory_object(aip_dir)
        except Exception as err:
            self.logger.warning("???")
            self.logger.error(err)
            raise #TODO: raise what?

        # ???
        mets = self._render_mets(timestamp = lambda: datetime.utcnow().isoformat() + "Z", 
                folders = aip_obj.dirs, 
                files = aip_obj.files,
                graph = "\n" + aip_obj.rdirs.ls(),
                events = self.preservation_events)
        mets = etree.tostring(mets, pretty_print=True, encoding=self.charset).decode(
                self.charset)
        
        # ???
        mets_file = "{}.mets.xml".format(self.account_id)
        mets_path = os.path.join(self._abspath(self.destination_dir), self.account_id,
                mets_file)
        
        # ???
        with open(mets_path, "w", encoding=self.charset) as mf:
            mf.write(mets)
            
        return mets_path


# TEST.
if __name__ == "__main__":

    logging.basicConfig(level="DEBUG")

    p = Packager("foo", 
            "../tests/sample_files/hot_folder", 
            "../tests/sample_files",
            {"20180101":["fooevent", None]}, 
            "../mets_templates/test.xml")
    
    p.package()
    pass
