#!/usr/bin/env python3

""" This module contains a class for creating a read-only object representation of a file. """

# import modules.
import hashlib
import logging
import logging.config
import math
import mimetypes
import os
from datetime import datetime


class FileObject(object):
    """ A class for creating a read-only object representation of a file. 

    Attributes:
        - isfile (bool): True.
        - isdir (bool): False.
        - name (str): The relative path to @self.root_object's path.
        - basename (str): The plain version of @self.path.
        - abspath (str): The absolute version of @self.path.
        - created (str): The creation date as ISO 8601.
        - modified (str): The modified date as ISO 8601.
        - size (int): The size in bytes.
        - mimetype (function): Returns the mimetype.
        - checksum (function): Returns the checksum value (default: SHA-256).
    """


    def __init__(self, path, parent_object, root_object, index):
        """ Sets instance attributes.
        
        Args:
            - path (str): A path to an actual file.
            - parent_object (DirectoryObject): The parent folder to which the @path file 
            belongs.
            - root_object (DirectoryObject): The root or "master" folder under which the @path
            file resides.
            - index (int): The unique position identifier for the @path file within the 
            context of the @root_object.

        Raises:
            - FileNotFoundError: If @path is not an actual file path.
            - ValueError: If @checksum_algorithm is not supported.
        """
 
        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience function to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")

        # normalize @path and log status.
        path = self._normalize_path(path)
        self.logger.info("Initializing FileObject for: {}".format(path))        
        
        # verify @path is a file.
        if not os.path.isfile(path):
            msg = "Can't find: {}".format(path)
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        # set attributes.
        self.path = path
        self.parent_object = parent_object
        self.root_object = root_object
        self.index = index
    
        # set path attributes.
        self.isfile = True
        self.isdir = False
        self.name = self._normalize_path(os.path.relpath(self.path, 
            start=self.root_object.path))
        self.basename = os.path.basename(self.path)
        self.abspath = self._normalize_path(os.path.abspath(self.path))

        # set file metadata.
        _iso_date = lambda t: datetime.utcfromtimestamp(t).isoformat() + "Z"
        self.created = _iso_date(os.path.getctime(path))
        self.modified = _iso_date(os.path.getmtime(path))
        self.size = os.path.getsize(self.path)
        self.mimetype = self._get_mimetype
        self.checksum = self._get_checksum
    

    def _get_mimetype(self):
        """ Returns the MIME type for @self.path.
        
        Returns:
            str: The return value.
        """
        
        self.logger.debug("Guessing MIME type for: {}".format(self.abspath))
        mimetype = mimetypes.guess_type(self.abspath)
        
        if mimetype is None:
            mimetype = "application/octet-stream"
        else:
            mimetype = mimetype[0]

        self.logger.debug("MIME type: {}".format(mimetype))
        return mimetype


    def _get_checksum(self, checksum_algorithm="SHA-256", block_size=4096):
        """ Returns the checksum value for @self.path using @checksum_algorithm.

        Args:
            - checksum_algorithm (str): The SHA algorithm with which to calculate the checksum
            value. Use only SHA-1, SHA-256, SHA-384, or SHA-512.
            - block_size (int): The chunk size with which to iteratively read @self.abspath
            while calculating the checksum. If None, twenty times the block size of the chosen
            SHA algorithm will be used. For example, SHA-256 has a block size of 64, therefore
            the block size would be 1280 (20 * 64).
        
        Returns:
            str: The return value.
        """
        
        self.logger.debug("Calculating {} checksum value for: {}".format(
            checksum_algorithm, self.abspath)) 

        # set checksum function map.
        checksum_map = {"SHA-1": hashlib.sha1(), "SHA-256": hashlib.sha256(), 
                "SHA-384": hashlib.sha384(), "SHA-512": hashlib.sha512()}
        
        # verify that @checksum_algorithm is legal.
        if checksum_algorithm not in checksum_map:
            self.logger.warning("Algorithm '{}' is not supported; must be one of: {}".format(
                checksum_algorithm, list(checksum_map)))
            msg = "Unsupported checksum algorithm: {}".format(checksum_algorithm)
            self.logger.err(msg)
            raise ValueError(msg)

        # establish hashlib function and block size to use.
        sha = checksum_map[checksum_algorithm]
        if block_size is None:
            block_size = sha.block_size * 20

        # calculate attempts needed to get checksum. 
        remaining_chunks = round(self.size/block_size)
        self.logger.debug("File chunks to read: {}".format(remaining_chunks))

        # calculate number of times to log progress.
        divider = round(math.log10(remaining_chunks * 10))
        logging_interval = round(remaining_chunks/divider)

        # get checksum per "https://stackoverflow.com/a/1131255". 
        data = open(self.abspath, "rb")
        while True:
            
            # read next data chunk; break if none are left.
            chunk = data.read(block_size)
            if not chunk:
                break
            sha.update(chunk)
            remaining_chunks -= 1

            # log updates.
            if remaining_chunks > 0 and (remaining_chunks % logging_interval) == 0:
                self.logger.debug("Remaining file chunks to read: {}".format(
                    remaining_chunks))

        checksum = sha.hexdigest()

        self.logger.debug("{} checksum: {}".format(checksum_algorithm, checksum))
        return checksum

        
if __name__ == "__main__":
    pass
