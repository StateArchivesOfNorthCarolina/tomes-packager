""" ???

Todo:
    * Add try/except around hash function.
    * Need ISO/UTF offset time.
"""


# import modules.
import glob
import hashlib
import mimetypes
import os
from datetime import datetime


class FileObject(object):
    """ ??? """
    
    def __init__(self, path, index, root=None, checksum_algorithm="SHA-256"):
        """ Sets instance attributes.
        
        Args:
            - ???

        Raises:
            ValueError: ???
        """

        # ???
        if not os.path.isfile(path):
            raise FileNotFoundError

        # set attributes.
        self.path = path
        self.index = index
        self.root = root
        self.checksum_algorithm = checksum_algorithm 

        # ???
        self._checksum_map = {"SHA-1": hashlib.sha1, "SHA-256": hashlib.sha256, 
                "SHA-384": hashlib.sha384, "SHA-512": hashlib.sha512}
        if checksum_algorithm not in self._checksum_map:
            raise ValueError
            
        # ??? path data.
        normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")
        self.name = normalize_path(os.path.relpath(self.path, start=self.root))

        # file metadata.
        self._created = os.path.getctime(path)
        self.created = datetime.utcfromtimestamp(self._created).isoformat() + "Z"
        self.size = os.path.getsize(self.path)
        self.mimetype = self.get_mimetype()
        self.checksum = self.get_checksum()

    
    def get_mimetype(self):
        """ ??? """
        mimetype = mimetypes.guess_type(self.path)[0]
        if mimetype is None:
            mimetype = "application/octet-stream"

        return mimetype


    def get_checksum(self):
        """ ??? """
 
        with open(self.path, "rb") as fb:
            checksum = self._checksum_map[self.checksum_algorithm](fb.read())
            checksum = checksum.hexdigest()

        return checksum


if __name__ == "__main__":
    pass

