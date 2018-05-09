#!/usr/bin/env python3

""" This module contains a class for creating a read-only object representation of a file. """

# import modules.
import glob
import hashlib
import logging
import logging.config
import mimetypes
import os
from datetime import datetime


class FileObject(object):
    """ A class for creating a read-only object representation of a file. 

        Attributes:
            - isfile (bool): True.
            - isdir (bool): False.
            - name (str): The relative path to @self.root_object's path.
            - basename (str): The absolute path.
            - abspath (str): The absolute version of @self.path.
            - created (str): The creation date as ISO 8601.
            - modified (str): The modified date as ISO 8601.
            - size (int): The size in bytes.
            - mimetype (str): The mimetype.
            - checksum (str): The checksum value per @self.checksum_algorithm.
    """


    def __init__(self, path, parent_object, root_object, index, checksum_algorithm="SHA-256"):
        """ Sets instance attributes.
        
        Args:
            - path (str): A path to an actual file.
            - parent_object (FolderObject): The parent folder to which the @path file belongs.
            - root_object (FolderObject): The root or "master" folder under which the @path 
            file and its @parent_object reside.
            - index (int): The unique identifier for the @path file within the context of the
            @root_object.
            - checksum_algorithm (str): The SHA algorithm with which to calculate the @path
            file's checksum value. Use only SHA-1, SHA-256, SHA-384, or SHA-512.

        Raises:
            - FileNotFoundError: If @path is not an actual file path.
        """
 
        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

       # verify @path is a file.
        if not os.path.isfile(path):
            msg = "Can't find: {}".format(path)
            self.logger.error(msg)
            raise FileNotFoundError(msg)
        self.isfile = True
        self.isdir = False

        # convenience function to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")    

        # set attributes.
        self.path = self._normalize_path(path)
        self.parent_object = parent_object
        self.root_object = root_object
        self.index = index
        self.checksum_algorithm = checksum_algorithm
    
        # set path attributes.
        self.name = self._normalize_path(os.path.relpath(self.path, 
            start=self.root_object.path))
        self.basename = os.path.basename(self.path)
        self.abspath = self._normalize_path(os.path.abspath(self.path))

        # set file metadata.
        _iso_date = lambda t: datetime.utcfromtimestamp(t).isoformat() + "Z"
        self.created = _iso_date(os.path.getctime(path))
        self.modified = _iso_date(os.path.getmtime(path))
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


    def _get_checksum(self, block_size=4096):
        """ Returns the checksum value for @self.path using @self.checksum_algorithm.

        Args:
            - block_size (int): The chunk size with which to iteratively read @self.abspath
            while calculating the checksum. If None, twenty times the block size of the chosen
            SHA algorithm will be used. For example, SHA-256 has a block size of 64, therefore
            the block size would be 1280 (20 * 64).
        
        Returns:
            str: The return value.
            
        Raises:
             - ValueError: If @self.checksum_algorithm is illegal.
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
        if block_size is None:
            block_size = sha.block_size * 20

        # calculate attempts needed to get checksum. 
        remaining_chunks = round(self.size/block_size)

        # get checksum per "https://stackoverflow.com/a/1131255". 
        data = open(self.abspath, "rb")
        while True:
            
            # read next data chunk; break if none are left.
            chunk = data.read(block_size)
            if not chunk:
                break
            sha.update(chunk)
            remaining_chunks -= 1

            # log every 10th read.
            if remaining_chunks > 0 and (remaining_chunks % 10) == 0:
                self.logger.debug("Remaining file chunks to read: {}".format(
                    remaining_chunks))

        checksum = sha.hexdigest()

        self.logger.info("{} checksum: {}".format(self.checksum_algorithm, checksum))
        return checksum

        
if __name__ == "__main__":
    pass
