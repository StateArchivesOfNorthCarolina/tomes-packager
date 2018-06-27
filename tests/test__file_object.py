#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import hashlib
import json
import logging
import os
import plac
import unittest
import warnings
from tomes_packager.lib.directory_object import *
from tomes_packager.lib.file_object import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_FileObject(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_file = __file__
        self.sample_dir = os.path.dirname(self.sample_file)
        self.dir_obj = DirectoryObject(self.sample_dir)
        self.file_obj = FileObject(self.sample_file, self.dir_obj, self.dir_obj, 0)


    def test__mimetype(self):
        """ Is the MIME type for @self.file_obj correct? """
        
        # get mime via mimetypes.guess_type.
        mime = mimetypes.guess_type(self.sample_file)[0]
        
        # make sure the FileObject mimetype is the same.
        self.assertEqual(mime, self.file_obj.mimetype())


    def test__checksum(self):
        """ Is the SHA-1 hash for @self.file_obj correct? """
        
        # get SHA-1 value of @self.sample_file via hashlib.
        sha1 = hashlib.sha1()
        with open(self.sample_file, "rb") as f:
            sha1.update(f.read())
        sha1 = sha1.hexdigest()
        
        # get FileObject SHA-1 hash and suppress ResourceWarning in unittest.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sha1_obj = self.file_obj.checksum("SHA-1")

        # make sure hashes are equal.
        self.assertEqual(sha1, sha1_obj)


# CLI.
def main(filepath:("file path")):
    
    "Converts a file to a FolderObject and prints its attributes to screen as JSON.\
    \nexample: `py -3 test__file_object.py sample_files/sample_rdf.xlsx`"

    # convert @filepath to a FileObject.
    dir_obj = DirectoryObject(os.path.dirname(filepath))
    file_obj = FileObject(filepath, dir_obj, dir_obj, 0)
    
    # collect @file_obj attributes.
    fdict = {}
    for att in file_obj.__dict__:
        if att[0] == "_":
            continue
        try:
            val = getattr(file_obj, att)()
        except TypeError:
            val = getattr(file_obj, att)
        fdict[att] = str(val)
    
    # convert @fdict to JSON.
    js = json.dumps(fdict, indent=2)
    print(js)


if __name__ == "__main__":

    plac.call(main)