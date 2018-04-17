#!/usr/bin/env python3

""" This module contains a class to create a METS <fileGrp> tree for a given list of files.
The output can be integrated into a complete METS file's <fileSec> element."""

# import modules.
import hashlib
import logging
import logging.config
import mimetypes
import os
from datetime import datetime
from lxml import etree


class FileGrp():
    """ A class to create a METS <fileGrp> tree for a given list of files. The output can be
    integrated into a complete METS file's <fileSec> element. """


    def __init__(self, ns_prefix, ns_map, sha_hash=256):
        """ Set instance attributes. 
        
        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
            - sha_hash (int): The SHA hash algorithm to use. This value must be 1, 256, 384, 
            or 512.

        Raises:
            ValueError: If @sha_hash is invalid.
        """

        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map

        # map SHA algorithms to hashlib functions.
        self.sha_map = {1: hashlib.sha1, 256: hashlib.sha256, 384: hashlib.sha384, 
                512: hashlib.sha512 }
        
        # validate @sha_hash; set @self.sha_hash.
        if sha_hash not in self.sha_map.keys():
            sha_list = list(self.sha_map.keys())
            msg = "@sha_hash must be one of: {}".format(sha_list)
            self.logger.error(msg)
            raise ValueError(msg)
        else:
            self.sha_hash = sha_hash


    def fileGrp(self, filenames, basepath, identifier, attributes=None):
        """ Creates a METS <fileGrp> element for all local files in @filenames.

        Args:
            - filenames (list): The file paths from which to create a <fileGrp> element.
            - basepath (str): Each <file> element's <FLocat> value is relative to this path.
            - identifier (str): The ID attribute value to set.
            - attributes (dict): The optional attributes to set.
        
        Returns:
            lxml.etree._Element: The return value.
        """

        self.logger.info("Creating <fileGrp> element.")

        # get padding length for local file identifiers.
        pad_len = len(str(len(filenames))) + 1

        # create <fileGrp> element.
        fileGrp_el = etree.Element("{" + self.ns_map[self.ns_prefix] + "}fileGrp",
                nsmap=self.ns_map)
       
        # set optional attributes and ID attribute.
        if attributes is not None:
            self.logger.info("Appending attributes to <fileGrp> element.")            
            for k, v in attributes.items():
                fileGrp_el.set(k, v)
        fileGrp_el.set("ID", identifier)

        # add a sub-element for each file.
        self.logger.info("Appending <file> sub-elements to <fileGrp> element.")
        
        file_pos = 0
        for filename in filenames:  

            # create <file> element.
            file_el = etree.SubElement(fileGrp_el, "{" + self.ns_map[self.ns_prefix] +
                    "}file", nsmap=self.ns_map)
            
            # set simple attributes.
            file_size = os.path.getsize(filename)
            file_el.set("SIZE", str(file_size))
            filename_id = identifier + "_" + str(file_pos).zfill(pad_len)
            file_el.set("ID", filename_id)
            
            # get mimetype; set MIMETYPE attribute.
            mime = mimetypes.guess_type(filename)[0]
            if mime is not None:
                file_el.set("MIMETYPE", mime)

            # get file creation date; set CREATED attribute.
            file_created = os.path.getctime(filename)
            file_created = datetime.utcfromtimestamp(file_created).isoformat() + "Z"
            file_el.set("CREATED", file_created)

            # get checksum; set CHECKSUM attribute.
            try:
                with open(filename, "rb") as f:
                    fb = f.read()
                checksum = self.sha_map[self.sha_hash](fb)
                checksum = checksum.hexdigest()
                file_el.set("CHECKSUM", checksum)
                file_el.set("CHECKSUMTYPE", "SHA-" + str(self.sha_hash))
            except (OSError, PermissionError) as err:
                self.logger.warning("Unable to get checksum for: {}".format(filename))
                self.logger.error(err)

            # create <FLocat> element; set attributes.
            filename = os.path.relpath(filename, basepath)
            filename = os.path.normpath(filename)
            flocat_el = etree.SubElement(file_el, "{" + self.ns_map[self.ns_prefix] +
                    "}FLocat", nsmap=self.ns_map)
            flocat_el.set("{" + self.ns_map["xlink"] + "}href", filename)
            flocat_el.set("LOCTYPE", "OTHER")
            flocat_el.set("OTHERLOCTYPE", "SYSTEM")
        
            file_pos += 1

        return fileGrp_el


if __name__ == "__main__":
    pass

