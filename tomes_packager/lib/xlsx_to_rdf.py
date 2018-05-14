#!/usr/bin/env python3

"""
This module contains a class for creating RDF/Dublin Core XML metadata from a Microsoft Excel
2010 file (.xlsx). """

# import modules.
import hashlib
import logging
import logging.config
import os
import rdflib
import xml.sax._exceptions
from datetime import datetime
from lxml import etree
from openpyxl import load_workbook


class XLSXToRDF():
    """ A class for creating RDF/Dublin Core XML metadata from a Microsoft Excel 2010 file 
    (.xlsx).
        
    Example:
        >>> xlsx = "../../tests/sample_files/sample_rdf.xlsx"
        >>> x2r = XLSXToRDF()
        >>> rdfs = x2r.get_rdfs(xlsx)
        >>> for rdf in rdfs:
        >>>     print(rdf.name)
        >>>     print(rdf.element)
        >>>     print(rdf.xml) 
    """


    def __init__(self, element_header="dc_element", value_header="dc_value", charset="utf-8"):
        """ Sets instance attributes.

        Args:
            - element_header (str): The worksheet header string for Dublin Core element names.
            - value_header (str): The worksheet header string for Dublin Core element values.
            - charset (str): The encoding to use for RDF XML strings.
        """
        
        # set logging; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.element_header = element_header
        self.value_header = value_header
        self.charset = charset
        
        # set namespace attributes.
        self.rdf_prefix = "rdf"
        self.dc_prefix = "dc"
        self.ns_map = {self.rdf_prefix: "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                self.dc_prefix: "http://purl.org/dc/elements/1.1/"}


    @staticmethod
    def _legalize_xml_text(xtext):
        """ A static method that alters @xtext by replacing vertical tabs, form feeds, and
        carriage returns with line breaks and by removing control characters except for line 
        breaks and tabs. This is so that @xtext can be written to XML without raising a 
        ValueError.
        
        Args:
            - xtext (str): The text to alter.

        Returns:
            str: The return value.
        """

        # legalize @xtext.
        for ws in ["\f","\r","\v"]:
            xtext = xtext.replace(ws, "\n")
        xtext = "".join([char for char in xtext if unicodedata.category(char)[0] != "C" or
            char in ("\t", "\n")])
        
        return xtex


    def _get_worksheets(self, xlsx_file):
        """ Gets the worksheets in @xlsx_file. Each worksheet's name must contain only letters
        and underscores.
        
        Args:
            - xlsx_file (str): The Excel file from which to obtain worksheets.
                
        Returns:
            list: The return value.
            Each item is an openpyxl.worksheet.worksheet.Worksheet.

        Raises:
            - OSError: If @xlsx_file can't be opened.
        """
   
        self.logger.info("Opening workbook: {}".format(xlsx_file))

        # load data from @xlsx_file.
        try:
            workbook = load_workbook(xlsx_file, read_only=False, data_only=True)
        except Exception as err:
            self.logger.warning("Can't open Excel file: {}".format(xlsx_file))
            self.logger.error(err)
            raise OSError(err)

        # collect candidate worksheets.
        self.logger.info("Looking for worksheets to convert to RDF.")
        worksheets = []
        for worksheet in workbook.worksheets:
            
            # only store worksheets with valid names.
            title = worksheet.title
            title_plain = title.replace("_", "")
            if title_plain.isalpha():
                self.logger.info("Found candidate worksheet: {}".format(title))
                worksheets.append(worksheet)
            else:
                self.logger.warning("Worksheet '{}' has an invalid name; skipping.".format(
                    title))
                illegal_chars = [c for c in title_plain if not c.isalpha()]
                self.logger.debug("Illegal characters found in '{}': {}".format(title, 
                    illegal_chars))

        return worksheets
 

    def _get_header_map(self, worksheet):
        """ Gets the headers in a given @worksheet.
        
        Args:
            worksheet (openpyxl.worksheet.worksheet.Worksheet): The worksheet object from
            which to obtain headers.
                
        Returns:
            dict: The return value.
            Each key is a header row's text. Each value is the corresponding column letter.
        """

        self.logger.info("Looking for metadata in worksheet: {}".format(worksheet.title))
        
        # create dict with header data.
        headers = [(header.value, header.column) for header in worksheet[1:1]]
        header_fields = tuple([h for h,v in headers])
        header_map = dict(headers)

        self.logger.info("Found the following headers: {}".format(header_fields))
        return header_map


    def _validate_header(self, header_map):
        """ Determines if @header_map contains the required headers: @self.element_header
        and @self.value_header.
        
        Args:
            - header_map (dict): Each key is a header row's text. Each value is the 
            corresponding column letter.            
        
        Returns:
            bool: The return value.
            True if the header is valid. Otherwise, False.
        """
        
        self.logger.info("Checking header validity.")
        is_valid = True

        # check for required fields.
        required_fields = [self.element_header, self.value_header]
        for required_field in required_fields:
            if required_field not in header_map.keys():
                self.logger.warning("Missing required field: {}".format(required_field))
                is_valid = False
        
        # report on validity.
        if is_valid:
            self.logger.info("Header is valid.")
        else:
            self.logger.warning("Header is invalid.")
        
        return is_valid


    def _get_rdf(self, worksheet):
        """ Generates an RDF XML element from a given @worksheet.
        
        Args:
            - worksheet (openpyxl.worksheet.worksheet.Worksheet): The worksheet from which to
            build and RDF XML element.
            
        Returns:
            lxml.etree._Element: The return value.
        """
     
        # get @worksheet header.
        header_map = self._get_header_map(worksheet)
            
        # if the header is not valid, return None.
        if not self._validate_header(header_map):
            self.logger.warning("Skipping invalid worksheet: {}".format(worksheet.title))
            return None
        else:
            self.logger.info("Building RDF tree from worksheet: {}".format(worksheet.title))
            
        # collect column data for element and element value fields.
        metadata = []
        for header in [self.element_header, self.value_header]:
            header_column = header_map[header]
            column = [cell.value for cell in worksheet[header_column][1:]]
            metadata.append(column)

        # create and identifier bash using the checksum of the metadata itself along with the
        # current timestamp.
        rdf_id = "{}".format(metadata) + datetime.utcnow().isoformat()
        rdf_id = rdf_id.encode(self.charset)
        rdf_id = "_" + hashlib.sha256(rdf_id).hexdigest()[:7]
        self.logger.debug("Created @rdf_id: {}".format(rdf_id))        
            
        # create RDF root as an lxml.etree._Element.
        rdf = etree.Element("{" + self.ns_map[self.rdf_prefix] + "}RDF", nsmap=self.ns_map)
        rdf_description = etree.Element("{" + self.ns_map[self.rdf_prefix] + "}Description", 
                nsmap=self.ns_map)
        rdf_description.set("{" + self.ns_map[self.rdf_prefix] + "}ID", rdf_id)
        
        # append sub-elements to @rdf.
        elements, values = metadata[0], metadata[1]
        for i in range(0, len(elements)):
            
            element, value = elements[i], values[i]
            
            # if either the element or value cell is blank, skip the row.
            if element is None or value is None:
                self.logger.warning("Skipping row {}; contains empty data.".format(i))
                continue
            else:
                self.logger.info("Creating element '{}' with value: {}".format(element,
                    value))
            
            # create sub-element and append it the RDF tree.
            dc_el = etree.Element("{" + self.ns_map[self.dc_prefix] + "}" + element, 
                    nsmap=self.ns_map)
            rdf_description.append(dc_el)            

            # set @element text to @value.
            value = str(value)
            try:
                dc_el.text = value
            except ValueError as err:
                self.logger.error(err)
                self.logger.info("Cleaning whitespace for element value.")
                dc_el.text = self._legalize_xml_text(value)
            
        # finalize @rdf.
        rdf.append(rdf_description)
        
        return rdf


    def validate_rdf(self, rdf):
        """ Determines if @rdf is well-formed XML and has valid RDF syntax.
        
        Args:
            - rdf (str): The RDF XML string to validate.
            
        Returns:
            bool: The return value.
            True if @rdf is valid. Otherwise, False.
        """

        # assume validity.
        is_valid = True

        # test if @rdf is malformed and/or not a valid RDF document.
        try:
            graph = rdflib.Graph()
            result = graph.parse(data=rdf, format="application/rdf+xml")
        except xml.sax._exceptions.SAXParseException as err:
            self.logger.warning("XML is malformed.")
            self.logger.error(err)
            is_valid = False
        except rdflib.exceptions.ParserError as err:
            self.logger.warning("XML is well-formed but the RDF syntax is wrong.")
            self.logger.error(err)
            is_valid = False

        # log malformed XML for debugging purposes.
        if not is_valid:
            self.logger.debug("Invalid RDF tree: {}".format(repr(rdf)))

        return is_valid

        
    def get_rdfs(self, xlsx_file):
        """ Creates RDF XML documents for each suitable worksheet in @xlsx_file.
        
        Args:
            - xlsx_file (str): The XML file from which to generate RDF XML.
                
        Returns:
            list: The return value.
            Each item is an object with three attributes: 
                1. name: The name of a corresponding worksheet in @xlsx_file.
                2. element: The RDF XML version of the worksheet as an lxml.etree._Element. 
                3. xml: The RDF XML as a string.

        Raises:
            - FileNotFoundError: If @xlsx_file is not a file. 
        """

        # verify @xlsx_file exists.
        if not os.path.isfile(xlsx_file):
            msg = "Can't find Excel file: {}".format(xlsx_file)
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        # create output container.
        rdfs = []
        
        # @rdfs will contain instances of this class. 
        class RDFObject(object):
            def __init__(self, name, element, _charset=self.charset):
                self.name, self.element = name, element
                self.xml = etree.tostring(rdf, pretty_print=True).decode(_charset)

        # for each worksheet; try to generate RDF.
        worksheets = self._get_worksheets(xlsx_file)
        for worksheet in worksheets:
            
            # make RDF.
            rdf = self._get_rdf(worksheet)
            if rdf is None:
                continue
            
            # make an RDFObject.
            rdfobj = RDFObject(worksheet.title, rdf)

            # only append valid RDF to @rdfs.
            if self.validate_rdf(rdfobj.xml):
                rdfs.append(rdfobj)

        return rdfs


if __name__ == "__main__":
    pass
