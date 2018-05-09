#!/usr/bin/env python3

"""
This module contains a class for creating RDF/Dublin Core metadata from a Microsoft Excel 2010
file (.xlsx).

Todo:
    * Add logging.
    * Get rid of __main__ test once you've created a unit test and know how this works! :-)
    * Can you add validation per XSD?
"""

# import modules.
import hashlib
import logging
import logging.config
import os
from datetime import datetime
from lxml import etree
from openpyxl import load_workbook


class XLSXToRDF():
    """ A class for creating RDF/Dublin Core metadata from a Microsoft Excel 2010 file 
    (.xlsx). """


    def __init__(self, element_header="dc_element", value_header="dc_value"):
        """ 
        Args:
            - ???
    
        """
        
        # set logging; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # ???
        self.element_header = element_header
        self.value_header = value_header
        
        # ???
        self.rdf_prefix = "rdf"
        self.dc_prefix = "dc"
        self.ns_map = {self.rdf_prefix: "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                self.dc_prefix: "http://purl.org/dc/elements/1.1/"}

    # ???
    def _get_worksheets(self, xlsx_file):
        """ ??? """
   
        self.logger.info("Opening workbook '{}'.".format(xlsx_file))

        # TODO: do try/except here and log if you can't open the file.
        workbook = load_workbook(xlsx_file, read_only=False, data_only=True)
        worksheets = workbook.worksheets

        return worksheets
 

    def _get_header_map(self, worksheet):
        """ ??? """

        self.logger.info("Looking for metadata in worksheet '{}'.".format(worksheet.title))
        
        header_map = [(header.value, header.column) for header in worksheet[1:1]]
        header_map = dict(header_map)

        logging.debug("Found headers: {}".format(header_map))
        return header_map


    def _validate_header(self, header_map):
        """ ??? """
        
        # ???
        if self.element_header not in header_map.keys():
            self.logger.warning("Invalid sheet; missing required header: {}".format(
                self.element_header))
            return False
        if self.value_header not in header_map.keys():
            self.logger.warning("Invalid sheet; missing required header: {}".format(
                self.value_header))
            return False
        
        logging.info("Header is valid.")
        return True


    def _get_rdf_el(self, header_map, worksheet):
        """ ??? """
    
        # ???
        metadata = []
        for header in [self.element_header, self.value_header]:
            header_column = header_map[header]
            column = [cell.value for cell in worksheet[header_column][1:]]
            metadata.append(column)

        # ???
        rdf_id = "{}".format(metadata) + datetime.utcnow().isoformat()
        rdf_id = rdf_id.encode("utf-8")
        logging.debug("Unhashed metadata + timestamp: {}".format(rdf_id))  
        rdf_id = "_" + hashlib.sha256(rdf_id).hexdigest()
        logging.debug("Hashed metadata + timestamp: {}".format(rdf_id))        
            
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
        self.logger.info("RDF tree built.")

        return rdf_el


    def get_RDFs(self, xlsx_file):
        """ ??? """

        RDFs = []

        worksheets = self._get_worksheets(xlsx_file)
        for worksheet in worksheets:
            header_map = self._get_header_map(worksheet)
            is_valid = self._validate_header(header_map)
            if not is_valid:
                self.logger.warning("Skipping sheet ...")
                continue
            else:
                RDFs.append(self._get_rdf_el(header_map, worksheet))

        return RDFs


# TEST.
if __name__ == "__main__":

    x2r = XLSXToRDF()
    f = "../../tests/sample_files/sample_rdf.xlsx"
    rdf = x2r.get_RDFs(f)
    rdf = [etree.tostring(r, pretty_print=True).decode() for r in rdf]
    print(rdf)
