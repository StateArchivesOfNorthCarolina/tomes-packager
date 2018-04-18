#!/usr/bin/env python3

"""
This module contains a class with covenience methods for creating METS files.

Todo:
    * Note that struct-links and behavior elements aren't supported.
    * Say this is for METS version 1.11.
        - Doesn't the default for @xsd already tell me that?
    * get_fileIDs() seems to be slowing things down. It seemed faster when I used the "*"
    instead of the specific METS namespace URI.
    * Pass the SHA type along from here (add to init).
    * Do you want to add a base64 convenience method to help wrap a <binData> value?
    * The template thing needs to add in GLOBAL "PYMETS" keys: DAY, ISO_LOCAL, ISO_GMT, 
    UnixTime as well as hashes of all those values so that one can make unique_ids on the fly:
    {PYMETS.day.hash}_copy. Actually you'll want the times at instantiation to be set. You'll
    also want real time values.
"""

# import modules.
import sys; sys.path.append("..")
import codecs
import jinja2
import logging
import logging.config
import os
from lxml import etree
from pymets.lib import anyElement
from pymets.lib import div
from pymets.lib import fileGrp
from pymets.lib import namespaces


class PyMETS():
    """ A class with covenience methods for creating METS files.
    
    Example:
    >>> from glob import glob
    >>> pymets = PyMETS()
    >>> root = pymets.make("mets") # create METS root.
    >>> header = pymets.make("metsHdr")
    >>> root.append(header)
    >>> attributes = {"ROLE":"CREATOR", "TYPE":"OTHER",  "OTHERTYPE":"Software Agent"}
    >>> agent = pymets.make("agent", attributes=attributes)
    >>> header.append(agent)
    >>> name = pymets.make("name")
    >>> name.text = "PyMETS"
    >>> agent.append(name)
    >>> fileSec = pymets.make("fileSec")
    >>> root.append(fileSec)
    >>> fileGrp = pymets.fileGrp(filenames=glob("./*.*"), basepath=".", identifier="demo")
    >>> fileSec.append(fileGrp)
    >>> structMap = pymets.make("structMap")
    >>> root.append(structMap)
    >>> div = pymets.div(fileSec)
    >>> structMap.append(div)
    >>> pymets.stringify(root) # string version of METS.
    '<mets:mets xmlns:mets="http://www.loc.gov/METS/"
    ...
    </mets:mets>\n'
    >>> pymets.validate(root) # True|False.
    """

    
    def __init__(self, ns_prefix="mets", ns_map=namespaces.mets, xsd_file=None, 
            sha_hash=256):
        """ Sets instance attributes.

        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
            This must at least contain an item where @ns_prefix is the key.
            - xsd_file (str): The filepath for the METS XSD.
            - sha_hash (int): ???
        """

        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map
        self.sha_hash = sha_hash

        # use default XSD if none provided.
        if xsd_file is None:
            xsd_file = os.path.dirname(__file__) + "/mets_1-11.xsd"
            self.logger.info("Setting XSD to: {}".format(xsd_file))
        self.xsd_file = xsd_file
        
        # get functions for writing CDATA blocks and XML comments.
        self.CDATA = etree.CDATA
        self.Comment = etree.Comment

        # compose instances of helper classes.
        self.AnyElement = anyElement.AnyElement(self.ns_prefix, self.ns_map)
        self.Div = div.Div(self.ns_prefix, self.ns_map)
        self.FileGrp = fileGrp.FileGrp(self.ns_prefix, self.ns_map, self.sha_hash)


    def load(self, xml, is_raw=False):
        """ Loads @xml file or XML string (@is_raw==True) as lxml.etree._Element.
        
        Args:
            - xml (str): The file or string to load.
            - is_raw (bool): Use True to load a string, False to load a file.
            
        Returns:
            lxml.etree._Element: The return value.
        """
        
        # set custom parser.
        parser = etree.XMLParser(remove_blank_text=True)
        
        # load string or file as needed.
        if is_raw:
            loaded_el = etree.fromstring(xml, parser)
        else:
            loaded_el = etree.parse(xml, parser).getroot()
        
        return loaded_el


    def load_template(self, xml, charset="utf-8", *args, **kwargs):
        """ Loads an @xml string after formatting the string using the
        string.Formatter.format() with for *args and **kwargs.
        ??? now using jinja2 so update ???
        
        Args:
            - xml (str): The ??? STRING OR ??? file to load.
            - charset (str): The optional encoding with which to load the file.
            - *args/**kwargs: The optional arguments to pass to the string formatter.
            
        Returns:
            lxml.etree._Element: The return value.
        """

        # read file as string; format it.
        if os.path.isfile(xml):
            with codecs.open(xml, encoding=charset) as xf:
                xml = xf.read()
        template = jinja2.Template(xml)
        rendered_template = template.render(*args, **kwargs)
        
        # load string as etree._Element.
        template_el = self.load(rendered_template, is_raw=True)
        return template_el


    def stringify(self, element, beautify=True, charset="utf-8"):
        """ Returns a string version for a given XML @element.
        
        Args:
            - element (lxml.etree._Element):
            - beautify (bool): Use True to pretty print.
            - charset (str): The character encoding for the returned string.

        Returns:
            str: The return value.
        """

        xstring = etree.tostring(element, pretty_print=beautify)
        xstring = xstring.decode(charset)
        
        return xstring


    def validate(self, xdoc):
        """ Validates @xdoc file against METS XSD.
        
        Args:
            - xdoc (str): The file to validate.
            
        Returns:
            bool: The return value. True for valid, otherwise False.
        """
        
        # load XSD.
        xsd = self.load(self.xsd_file, False)
        validator = etree.XMLSchema(xsd)
        
        # validate.
        is_valid = validator.validate(xdoc)
        return is_valid


    def make(self, *args, **kwargs):
        """ Returns an etree element using the self.AnyElement instance.
        
        Returns:
            lxml.etree._Element: The return value.
        """

        name_el = self.AnyElement.anyElement(*args, **kwargs)
        return name_el


    def div(self, *args, **kwargs):
        """ Returns a METS <div> etree element using the self.Div instance.

        Returns:
            lxml.etree._Element: The return value.
        """

        div_el = self.Div.div(*args, **kwargs)
        return div_el


    def fileGrp(self, *args, **kwargs):
        """ Returns a METS <fileGrp> etree element using the self.FileGrp instance.
        
        Returns:
            lxml.etree._Element: The return value.
        """

        filegrp_el = self.FileGrp.fileGrp(*args, **kwargs)
        return filegrp_el


    def wrap(self, xtree, mdtype, attributes={}, xmlData=True):
        """ Wraps etree element (@xtree) in an <mdWrap/xmlData|binData> etree element.
        
        Args:
            - xtree (lxml.etree._Element): An etree XML element.
            - mdtype (str): The required "MDTYPE" attribute for the <mdWrap> element.
            - attributes (dict): The optional attributes to set.
            - xmlData (bool): Use True to wrap @xtree within a parent <xmlData> element.
            Use false to wrap a parent <binData> element.
            
        Returns:
            lxml.etree._Element: The return value.
        """
        
        # add/overwrite @mdtype to attributes; make root element.
        attributes["MDTYPE"] = mdtype
        wrap_el = self.make("mdWrap", attributes)

        # set parent for @xtree.
        if xmlData:
            xobdata_el = self.make("xmlData")
        else:
            xobdata_el = self.make("binData")
        
        # wrap @xtree.
        xobdata_el.append(xtree)
        wrap_el.append(xobdata_el)
        
        return wrap_el
        

if __name__ == "__main__":
    pass

