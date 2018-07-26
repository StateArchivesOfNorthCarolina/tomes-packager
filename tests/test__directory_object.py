#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import glob
import logging
import os
import plac
import unittest
from tomes_packager.lib.directory_object import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_DirectoryObject(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_dir = os.path.dirname(__file__)
        self.dir_obj = DirectoryObject(self.sample_dir)


    def test__dirs(self):
        """ Does @self.dir_obj.dirs yield the same folders as glob? """

        # get folder basenames via glob and @DirectoryObject.dirs.
        glob_dirs = [os.path.basename(f) for f in glob.glob("**", recursive=False) 
                if os.path.isdir(f)]
        obj_dirs = [f.basename for f in self.dir_obj.dirs()]

        # make sure they are equal.
        self.assertEqual(glob_dirs.sort(), obj_dirs.sort())
        

    def test__rdirs(self):
        """ Does @self.dir_obj.rdirs yield the same folders as glob? """

        # get folder basenames via glob and @DirectoryObject.rdirs.
        glob_dirs = [os.path.basename(f) for f in glob.glob("**", recursive=True) 
                if os.path.isdir(f)]
        obj_dirs = [f.basename for f in self.dir_obj.rdirs()]

        # make sure they are equal.
        self.assertEqual(glob_dirs.sort(), obj_dirs.sort())


    def test__files(self):
        """ Does @self.dir_obj.files yield the same files as glob? """

        # get file basenames via glob and @DirectoryObject.files.
        glob_files = [os.path.basename(f) for f in glob.glob("**", recursive=False) 
                if os.path.isfile(f)]
        obj_files = [f.basename for f in self.dir_obj.files()]

        # make sure they are equal.
        self.assertEqual(glob_files.sort(), obj_files.sort())


    def test__rfiles(self):
        """ Does @self.dir_obj.rfiles yield the same files as glob? """

        # get file basenames via glob and @DirectoryObject.rfiles.
        glob_files = [os.path.basename(f) for f in glob.glob("**", recursive=True) 
                if os.path.isfile(f)]
        obj_files = [f.basename for f in self.dir_obj.rfiles()]

        # make sure they are equal.
        self.assertEqual(glob_files.sort(), obj_files.sort())


# CLI.
def main(folder:("folder path")):
    
    "Converts a folder to a DirectoryObject and prints a visualization to screen.\
    \nexample: `python3 test__directory_object.py sample_files`"

    # convert @folder to a DirectoryObject.
    dir_obj = DirectoryObject(folder)
    
    # print graph of @folder.
    for line in dir_obj.graph():
        print(line)


if __name__ == "__main__":
    plac.call(main)