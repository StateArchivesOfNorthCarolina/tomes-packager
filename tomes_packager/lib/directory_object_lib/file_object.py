#!/usr/bin/env python3

""" This module contains a class for converting a file path into an object. """

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
        self.mimetype = self._get_mimetype()
        self.checksum = self._get_checksum()

    
    def _get_mimetype(self):
        """ Returns the MIME type for @self.path.
        
        Returns:
            str: The return value.
        """
        
        self.logger.info("Guessing MIME type for: {}".format(self.abspath))
        mimetype = mimetypes.guess_type(self.abspath)[0]
        
        if mimetype is None:
            mimetype = "application/octet-stream"

        return mimetype


    def _get_checksum(self, block_size=2048):
        """ Returns the checksum value for @self.path using @self.checksum_algorithm.

        Args:
            - block_size (int): The chunk size with which to iteratively read @self.abspath
            while calculating the checksum. If None, ten times the block size of the chosen
            SHA algorithm will be used (ex: SHA-256 has a block size of 64, therefore 640).
        
        Returns:
            str: The return value.
            
        Raises:
             ValueError: If @self.checksum_algorithm is illegal.
        """

        # assigning hash names to hash functions.
        checksum_map = {"SHA-1": hashlib.sha1(), "SHA-256": hashlib.sha256(), 
                "SHA-384": hashlib.sha384(), "SHA-512": hashlib.sha512()}
        
        # verify that @self.checksum_algorithm is legal
        if self.checksum_algorithm not in checksum_map:
            self.logger.warning("Algorithm '{}' is not valid; must be one of: {}".format(
                self.checksum_algorithh, checksum_map.keys()))
            msg = "Illegal checksum algorithm: {}".format(self.checksum_algorith)
            self.logger.err(msg)
            raise ValueError(msg)
        
        self.logger.info("Calculating {} checksum value for: {}".format(
            self.checksum_algorithm, self.abspath))

        # establish hashlib function and block size to use.
        sha = checksum_map[self.checksum_algorithm]
        block_size = sha.block_size * 10

        # get checksum per "https://stackoverflow.com/a/1131255". 
        data = open(self.abspath, "rb")
        remaining_blocks = self.size
        while True:
            chunk = data.read(block_size)
            if not chunk:
                break
            sha.update(chunk)
            remaining_blocks -= block_size
            if remaining_blocks > 0:
                self.logger.debug("Remaining blocks to read: {}.".format(remaining_blocks))            
        checksum = sha.hexdigest()

        return checksum

        
if __name__ == "__main__":
    pass
