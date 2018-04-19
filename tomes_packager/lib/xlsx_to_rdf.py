#!/usr/bin/env python3

"""
This module contains a class??? for creating RDF/Dublin Core metadata from a Microsoft Excel
2010 file (.xlsx).

Todo:
    * Make this a class.
    * Add logging.
"""

# import modules.
import sys; sys.path.append("..")
import hashlib
import logging
import logging.config
from datetime import datetime
import os
from openpyxl import load_workbook
from pymets import mets
from pymets.lib.namespaces import rdf_dc


def excel_to_rdf(xlsx_path, element_header="dc_element", value_header="dc_value"):
    """ A function for creating RDF/Dublin Core metadata from a Microsoft Excel 2010 file 
    (.xlsx). 
    
    Args:
        - ???
    
    """
    
    # set logging; suppress logging by default. 
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    
    # ???
    ns_prefix = "rdf"
    ns_map = rdf_dc

    # ???
    pymets = mets.PyMETS(ns_prefix, ns_map)

    # ???
    logging.info("Opening workbook '{}'.".format(xlsx_path))
    # do try/except here and log if you can't open the file.
    workbook = load_workbook(xlsx_path, read_only=False, data_only=True)
    worksheets = workbook.get_sheet_names()

    for worksheet in worksheets:
        
        logging.info("Looking for metadata in worksheet '{}'.".format(worksheet))
        worksheet_object = workbook[worksheet]
        header_map = [(header.value, header.column) for header in worksheet_object[1:1]]
        header_map = dict(header_map)
        logging.debug("Found headers: {}".format(header_map))
        
        # ???
        if element_header not in header_map.keys():
            logging.info("Skipping worksheet. Missing required header '{}'.".format(
                element_header))
            continue
        elif value_header not in header_map.keys():
            logging.info("Skipping sheet. Missing required header '{}.'".format(
                value_header))
            continue
        else: 
            logging.info("Found required headers: {}".format((element_header, value_header)))

        # ???
        metadata = []
        for header in [element_header, value_header]:
            header_column = header_map[header]
            column = [cell.value for cell in worksheet_object[header_column][1:]]
            metadata.append(column)

        # ??? paranoid check.
        elements, values = metadata[0], metadata[1]
        if not len(elements) == len(values):
            logging.warning("Skipping sheet. Length of '{}' and '{}' do not match.".format(
                element_header, value_header))
            continue

        # ???
        rdf_id = "{}".format(metadata) + datetime.utcnow().isoformat()
        rdf_id = rdf_id.encode("utf-8")
        logging.debug("Unhashed metadata + timestamp: {}".format(rdf_id))  
        rdf_id = "_" + hashlib.sha256(rdf_id).hexdigest()
        logging.debug("Hashed metadata + timestamp: {}".format(rdf_id))        
            
        # ???
        rdf_el = pymets.make("rdf:RDF")
        rdf_description = pymets.make("rdf:Description", {"rdf:ID":rdf_id})
        for i in range(0, len(elements)):
            element, value = elements[i], values[i]
            if element is not None and value is not None:
                element = pymets.make("dc:" + element)
                element.text = str(value)
                rdf_description.append(element)
            rdf_el.append(rdf_description)
        logging.info("RDF tree built.")

    return rdf_el


# TEST.
if __name__ == "__main__":

    pymets = mets.PyMETS()
    rdf_el = excel_to_rdf(os.path.dirname(__file__) + "/test.xlsx")
    rdf_doc = pymets.stringify(rdf_el)
    print(rdf_doc)
