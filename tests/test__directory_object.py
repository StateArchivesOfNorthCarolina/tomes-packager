#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import os
import unittest
from tomes_packager.lib.directory_object import *

# enable logging.
logging.basicConfig(level=logging.WARNING)


class Test_DirectoryObject(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_dir = os.path.dirname(__file__)


    def test__isdir(self):
        """ Is @self.sample_dir a folder? """
        
        # check if @self.sample_dir is a folder; create a DirectoryObject out of it.
        is_dir = os.path.isdir(self.sample_dir)
        dir_obj = DirectoryObject(self.sample_dir)        
        
        # make sure the object really is a folder.
        self.assertEquals(is_dir, dir_obj.isdir)


# CLI.
def main(folder:("folder path")):
    
    "Converts a folder to a DirectoryObject and prints a visualization to screen.\
    \nexample: `py -3 test__directory_object.py .`"

    # convet @events_log to a PREMISObject.
    dir_obj = DirectoryObject(folder)
    
    # print graph of @folder.
    for line in dir_obj.graph():
        print(line)


if __name__ == "__main__":

    import plac
    plac.call(main)
