#!/usr/bin/env python3

""" This module contains a class to create a METS <div> tree for a given list of files. The
output can be integrated into a complete METS file's <structMap> element. """

# import modules.
import logging
import logging.config
from lxml import etree


class Div():
    """ A class to create a METS <div> tree for a given list of files. The output can be
    integrated into a complete METS file's <structMap> element. """
    

    def __init__(self, ns_prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map


    def div(self, file_ids, attributes=None):
        """ Creates a METS <div> etree element for each item in @file_ids.

        Args:
            - file_ids (list): The identifiers to us for each <fptr> element within the <div>.
            - attributes (dict): The optional attributes to set.
        
        Returns:
            lxml.etree._Element: The return value.
        """
        
        self.logger.info("Creating <div> element.")

        # create <div> element.
        div_el = etree.Element("{" + self.ns_map[self.ns_prefix] + "}div",
                nsmap=self.ns_map)
        
        # set optional attributes.
        if attributes is not None:
            self.logger.info("Appending attributes to <div> element.".format(name))
            for k, v in attributes.items():
                div_el.set(k, v)

        # add <fprt> sub-elements with FILEID attribute.
        self.logger.info("Appending <fptr> sub-elements to <div> element.")
        for file_id in file_ids:
            fptr_el = etree.SubElement(div_el, "{" + self.ns_map[self.ns_prefix] + "}fptr",
                    nsmap=self.ns_map)
            fptr_el.set("FILEID", file_id)

        return div_el


if __name__ == "__main__":
    pass

