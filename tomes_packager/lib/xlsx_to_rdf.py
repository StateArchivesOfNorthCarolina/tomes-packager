#!/usr/bin/env python3

"""
This module contains a class for creating RDF/Dublin Core metadata from a Microsoft Excel 2010
file (.xlsx).

Todo:
    * Add docstrings/logging.
"""

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
    """ A class for creating RDF/Dublin Core metadata from a Microsoft Excel 2010 file 
    (.xlsx). 
    
        
    Example:
        >>> xlsx = "../../tests/sample_files/sample_rdf.xlsx"
        >>> x2r = XLSXToRDF()
        >>> rdfs = x2r.get_rdfs(f) # list of openpyxl worsheets.
        >>> for rdf in rdfs:
        >>>     print(rdf.title)
        >>>     print(rdf.rdf)
    """


    def __init__(self, element_header="dc_element", value_header="dc_value", charset="utf-8"):
        """ Sets instance attributes.

        Args:
            - element_header (str):
            - value_header (str):
            - charset (str): 
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


    def _get_worksheets(self, xlsx_file):
        """ ???
        
        Args:
            - xlsx_file (str):
                
        Returns:
            list: The return value.
            Each item is an openpyxl.worksheet.worksheet.Worksheet.
        """
   
        self.logger.info("Opening workbook: {}".format(xlsx_file))

        # ???
        try:
            workbook = load_workbook(xlsx_file, read_only=False, data_only=True)
        except Exception as err:
            # TODO: What exceptions?
            self.logger.warning("")
            self.logger.error("")
            raise

        # ???
        worksheets = []
        for worksheet in workbook.worksheets:
            
            # ???
            title = worksheet.title
            
            # ???
            if title.replace("_", "").isalpha:
                self.logger.info("{}".format(title))
                worksheets.append(worksheet)
            else:
                self.logger.warning("")

        return worksheets
 

    def _get_header_map(self, worksheet):
        """ ???
        
        Args:
            worksheet (openpyxl.worksheet.worksheet.Worksheet): 
                
        Returns:
            dict: The return value.
            ???
        """

        self.logger.info("Looking for metadata in worksheet '{}'.".format(worksheet.title))
        
        # ???
        header_map = [(header.value, header.column) for header in worksheet[1:1]]
        header_map = dict(header_map)
        
        logging.info("Found the following headers: {}".format(header_map))
        return header_map


    def _validate_header(self, header_map):
        """ ??? 
        
        Args:
            - header_map (dict): ???
            
        Returns:
            bool: The return value.
            ???
        """
        
        self.logger.info("")

        # ???
        if self.element_header not in header_map.keys():
            self.logger.warning("Invalid sheet; missing required header: {}".format(
                self.element_header))
            return False
        
        # ???
        if self.value_header not in header_map.keys():
            self.logger.warning("Invalid sheet; missing required header: {}".format(
                self.value_header))
            return False
        
        logging.info("Sheet headers are valid.")
        return True


    def _get_rdf(self, header_map, worksheet):
        """ ??? 
        
        Args:
            - header_map (dict):
            - worksheet (openpyxl.worksheet.worksheet.Worksheet):
            
        Returns:
            str: The return value.
            The RDF document.
        """
    
        self.logger.info("Building RDF tree from worksheet: {}".format(worksheet.title))
    
        # ???
        metadata = []
        for header in [self.element_header, self.value_header]:
            header_column = header_map[header]
            column = [cell.value for cell in worksheet[header_column][1:]]
            metadata.append(column)

        # ???
        rdf_id = "{}".format(metadata) + datetime.utcnow().isoformat()
        rdf_id = rdf_id.encode("utf-8")
        rdf_id = "_" + hashlib.sha256(rdf_id).hexdigest()
        self.logger.debug("Hashed metadata + timestamp: {}".format(rdf_id))        
            
        # ???
        rdf_el = etree.Element("{" + self.ns_map[self.rdf_prefix] + "}RDF", nsmap=self.ns_map)
        rdf_description = etree.Element("{" + self.ns_map[self.rdf_prefix] + "}Description", 
                nsmap=self.ns_map)
        rdf_description.set("{" + self.ns_map[self.rdf_prefix] + "}ID", rdf_id)
        
        # ???
        elements, values = metadata[0], metadata[1]
        for i in range(0, len(elements)):
            
            element, value = elements[i], values[i]
            
            # ???
            if element is None or value is None:
                self.logger.warning("Skipping ... ???")
                continue
            
            # ???
            dc_el= etree.Element("{" + self.ns_map[self.dc_prefix] + "}" + element, 
                    nsmap=self.ns_map)
            dc_el.text = str(value)
            rdf_description.append(dc_el)
        
        # ???
        rdf_el.append(rdf_description)
        rdf = etree.tostring(rdf_el, pretty_print=True).decode(self.charset)
        
        return rdf


    def validate_rdf(self, rdf):
        """ ???
        
        Args:
            - rdf (str):
            
        Returns:
            bool: The return value.
        """

        # ???
        is_valid = True

        # ???
        try:
            graph = rdflib.Graph()
            result = graph.parse(data=rdf, format="application/rdf+xml")
        except xml.sax._exceptions.SAXParseException as err:
            self.logger.warning("bad XML")
            self.logger.error(err)
            is_valid = False
        except rdflib.exceptions.ParserError as err:
            self.logger.warning("bad RDF")
            self.logger.error(err)
            is_valid = False

        return is_valid

        
    def get_rdfs(self, xlsx_file):
        """ ??? 
        
        Args:
            - xlsx_file (str):
                
        Returns:
            list: The return value.
            Each item is an openpyxl.worksheet.worksheet.Worksheet with an added "rdf"
            attribute. This attribute is an RDF document (str).
        """
            
        # create output container.
        rdfs = []
        

        # ???
        worksheets = self._get_worksheets(xlsx_file)
        for worksheet in worksheets:
            
            # ???
            header_map = self._get_header_map(worksheet)
            is_valid = self._validate_header(header_map)
            
            # ???
            if not is_valid:
                self.logger.warning("Skipping sheet ...")
                continue

            # ???
            rdf = self._get_rdf(header_map, worksheet)
            if self.validate_rdf(rdf):
                worksheet.__setattr__("rdf", rdf)
                rdfs.append(worksheet)

        return rdfs


# TEST.
if __name__ == "__main__":

    x2r = XLSXToRDF()
    f = "../../tests/sample_files/sample_rdf.xlsx"
    rdfs = x2r.get_rdfs(f)
    rdf = rdfs[0]
    print(rdf.title)
    print(rdf.rdf)
