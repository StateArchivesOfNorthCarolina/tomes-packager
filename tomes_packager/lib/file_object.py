""" ???

Todo:
    * Add try/except around hash function.
    * Need ISO/UTF offset time.
    * Checksum should be an attribute to avoid recalculation.
        - If the attribute doesn't exst, then set self.checksum.
"""


# import modules.
import glob
import hashlib
import mimetypes
import os
from datetime import datetime


class FileObject(object):
    """ ??? """
    
    def __init__(self, path, path_object, index, parent=None, checksum_algorithm="SHA-256"):
        """ Sets instance attributes.
        
        Args:
            - ???

        Raises:
            ValueError: ???
        """

        # ???
        if not os.path.isfile(path):
            raise FileNotFoundError
        self.isfile = True
        self.isdir = False

        # set attributes.
        self.path = path
        self.path_object = path_object
        self.index = index
        self.parent = parent
        self.checksum_algorithm = checksum_algorithm 
            
        # ??? path data.
        normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")
        self.name = normalize_path(os.path.relpath(self.path, start=self.parent))
        #self.name = os.path.basename(self.path)
        self.abspath = normalize_path(os.path.abspath(self.path))

        # file metadata.
        self._created = os.path.getctime(path)
        self.created = datetime.utcfromtimestamp(self._created).isoformat() + "Z"
        self.size = os.path.getsize(self.path)
        self.mimetype = self.get_mimetype()
        self.checksum = lambda: self.get_checksum()

    
    def get_mimetype(self):
        """ ??? """
        mimetype = mimetypes.guess_type(self.path)[0]
        if mimetype is None:
            mimetype = "application/octet-stream"

        return mimetype


    def get_checksum(self):
        """ ??? """

        checksum_map = {"SHA-1": hashlib.sha1, "SHA-256": hashlib.sha256, 
                "SHA-384": hashlib.sha384, "SHA-512": hashlib.sha512}
        if self.checksum_algorithm not in checksum_map:
            raise ValueError
        with open(self.path, "rb") as fb:
            checksum = checksum_map[self.checksum_algorithm](fb.read())
            checksum = checksum.hexdigest()

        return checksum


##    def __getattr__(self, attr):
##        if attr == "checksum":
##            return self.get_checksum()

        
if __name__ == "__main__":
    pass

