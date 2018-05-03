#!/usr/bin/env python3

""" This module contains a class for converting a file path into an object.

Todo:
    * I think it's important to only call checksum() when requested and ONLY call it once.
        - Also might want to test on large files.
"""

# import modules.
import glob
import hashlib
import logging
import logging.config
import mimetypes
import os
from datetime import datetime


class FileObject(object):
    """ A class for converting a file path into an object. """
    
    
    def __init__(self, path, parent_object, root_object, index, checksum_algorithm="SHA-256"):
        """ Sets instance attributes.
        
        Args:
            - path (str): A path to an actual file.
            - parent_object (FolderObject): The parent folder to which the @path file belongs.
            - root_object (FolderObject): The root or "master" FolderObject under which the 
            @path file and its @parent_object reside.
            - index (int): The unique identifier for the @path file within the context of the
            @root_object.
            - checksum_algorithm (str): The SHA algorithm with which to calculate the @path
            file's checksum value. Use only SHA-1, SHA-256, SHA-384, or SHA-512.

        Raises:
            FileNotFoundError: If @path is not an actual file path.
        """

        # verify @self.path is a file.
        if not os.path.isfile(path):
            raise FileNotFoundError
        self.isfile = True
        self.isdir = False

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience function to clean up path notation.
        self.normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")    

        # set attributes.
        self.path = self.normalize_path(path)
        self.parent_object = parent_object
        self.root_object = root_object
        self.index = index
        self.checksum_algorithm = checksum_algorithm 
    
        # set path attributes.
        self.name = self.normalize_path(os.path.relpath(self.path, 
            start=self.root_object.path))
        self.basename = os.path.basename(self.path)
        self.abspath = self.normalize_path(os.path.abspath(self.path))

        # set file metadata.
        iso_date = lambda t: datetime.utcfromtimestamp(t).isoformat() + "Z"
        self.created = iso_date(os.path.getctime(path))
        self.modified = iso_date(os.path.getmtime(path))
        self.size = os.path.getsize(self.path)
        self.mimetype = self.get_mimetype()
        self.checksum = self.get_checksum()

    
    def get_mimetype(self):
        """ Returns the MIME type for @self.path.
        
        Returns:
            str: The return value.
        """
        
        self.logger.info("Guessing MIME type for: {}".format(self.abspath))
        mimetype = mimetypes.guess_type(self.abspath)[0]
        
        if mimetype is None:
            mimetype = "application/octet-stream"

        return mimetype


    def get_checksum(self):
        """ Returns the checksum value for @self.path using @self.checksum_algorithm. 
        
        Returns:
            str: The return value.
            
        Raises:
             ValueError: If @self.checksum_algorithm is illegal.
        """

        # assing hash names to hash functions.
        checksum_map = {"SHA-1": hashlib.sha1, "SHA-256": hashlib.sha256, 
                "SHA-384": hashlib.sha384, "SHA-512": hashlib.sha512}
        
        # verify that @self.checksum_algorithm is legal
        if self.checksum_algorithm not in checksum_map:
            self.logger.warning("Algorithm '{}' is not valid; must be one of: {}".format(
                self.checksum_algorithh, checksum_map.keys()))
            msg = "Illegal checksum algorithm: {}".format(self.checksum_algorith)
            self.logger.err(msg)
            raise ValueError(msg)
        
        self.logger.info("Calculating {} checksum value for: {}".format(
            self.checksum_algorithm, self.abspath))

        # get checksum.
        with open(self.abspath, "rb") as fb:
            checksum = checksum_map[self.checksum_algorithm](fb.read())
            checksum = checksum.hexdigest()

        return checksum

        
if __name__ == "__main__":
    pass
