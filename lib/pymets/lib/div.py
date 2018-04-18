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


    def get_fileIDs(self, file_el):
        """ Returns a list of <fileGrp/file> @ID values for a given @file_el - an individual
        <fileGrp> or an entire <fileSec> element.
        
        Args:
            - @file_el (lxml.etree._Element): A <fileGrp> or <fileSec> lxml.etree._Element.
            
        Returns:
            list: The return value.
        """

        # set <file> path.
        path = "{" + self.ns_map[self.ns_prefix] + "}file"

        # make adjustments if @file_el is a <fileSec> element.
        if file_el.tag[-7:] == "fileSec":
            path = "*" + path
        
        # make list of @ID attributes.
        fids = [fid.get("ID") for fid in file_el.findall(path)]
        return fids



    def div(self, fileSec_el, attributes=None):
        """ Creates a METS <div> etree element for each item in @file_ids.

        Args:
            - fileSec_el (lxml.etree._Element): ???
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
                self.logger.info("Setting attribute '{}' with value '{}'.".format(k, v))
                div_el.set(k, v)

        # add <fprt> sub-elements with FILEID attribute.
        self.logger.info("Appending <fptr> sub-elements to <div> element.")
        for file_id in self.get_fileIDs(fileSec_el):
            fptr_el = etree.SubElement(div_el, "{" + self.ns_map[self.ns_prefix] + "}fptr",
                    nsmap=self.ns_map)
            fptr_el.set("FILEID", file_id)

        return div_el


if __name__ == "__main__":
    pass

