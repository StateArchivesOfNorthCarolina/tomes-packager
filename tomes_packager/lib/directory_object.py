#!/usr/bin/env python3

""" This module contains a class for creating a read-only object representation of a folder.

Todo:
    * FileObject and DirecttoryObkect still need parent names and basenames I think.
        - Just as strings and NOT objects. :-]
"""

# import modules.
import sys; sys.path.append("..")
import glob
import logging
import logging.config
import os
from datetime import datetime
from lib.directory_object_lib.file_object import FileObject


class DirectoryObject(object):
    """ A class for creating a read-only object representation of a folder. 
    
    Attributes:
        - isdir (bool): True.
        - isfile (bool): False.
        - abspath (str): The absolute version of @self.path.
        - name (str): The relative path to @self.root_object.
        - basename (str): The plain directory name.
        - depth (int): The distance from @self.root_object.
        - created (str): The creation date as ISO 8601.
        - modified (str): The modified date as ISO 8601.
        - dirs (generator): All subfolders (non-recursive) within @self.path. Each item is a
        DirectoryObject.
        - rdirs (generator): All subfolders (recursive) within @self.path. Each item is a 
        DirectoryObject.
        - files (generator): All files (non recursive) within @self.path. Each item is a 
        FileObject.
        - rfiles (generator): All files (recursive) within @self.path. Each item is a 
        FileObject.
    """


    def __init__(self, path, root_object=None):
        """ Sets instance attributes.
        
        Args:
            - path (str): A path to an actual folder.
            - root_object (DirectoryObject): The root or "master" folder under which the @path
            folder and its @parent_object reside.

        Raises:
            - NotADirectoryError: If @path is not an actual folder path.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # verify @path is a folder.
        if not os.path.isdir(path):
            msg = "Can't find: {}".format(path)
            self.logger.error(msg)
            raise NotADirectoryError(msg)
        self.isdir = True
        self.isfile = False
 
        # convenience function to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")  

        # set attributes.
        self.path = self._normalize_path(path)
        self.root_object = self if root_object is None else root_object
        
        # set path attributes.
        self.depth = self.path.count("/")#depth
        self.abspath = self._normalize_path(os.path.abspath(self.path))
        self.basename = os.path.basename(self.abspath)
        if root_object is not None:
            self.name = self._normalize_path(os.path.relpath(self.path, 
            start=self.root_object.path))
        else:
            self.name = self.basename

        # set folder metadata.
        _iso_date = lambda t: datetime.utcfromtimestamp(t).isoformat() + "Z"
        self.created = _iso_date(os.path.getctime(path))
        self.modified = _iso_date(os.path.getmtime(path))

        # add dependency attributes.
        self._file_object = FileObject

        # create generators for non-recursive and recursive files and folders.
        self.dirs = self._get_dirs()
        self.rdirs = self._get_dirs(True)
        self.files = self._get_files()
        self.rfiles = self._get_files(True)
    
    @classmethod
    def _this(cls, *args, **kwargs):
        """ Returns instance of this class. """

        return cls(*args, **kwargs)



    def _get_files(self, recursive=False):
        """ Creates ???.

        Args:
            - recursive (bool): ???

        Returns:
            generator: The return value.
        """

        #self.logger.info("???")
  
        def generate_file_obj():

            ndx = 0
            
            #for folder in self._path_object.glob(pattern):
            for dirpath, dirnames, filenames in os.walk(self.path):

                for filename in filenames:

                    if not recursive and self._normalize_path(dirpath) != self.path:
                        break
                    
                    filepath = os.path.join(dirpath, filename)
                    filepath = self._normalize_path(filepath)

                    file_obj = self._file_object(filepath, self.root_object, ndx)

                    yield file_obj
                    ndx += 1

        return generate_file_obj()

    
    def _get_dirs(self, recursive=False):
        """ Creates DirectoryObject instances for each folder @self directory.

        Args:
            - recursive (bool): ???

        Returns:
            generator: The return value.
        """

        #self.logger.info("???")
  
        def generate_dir_objs():
  
            #for folder in self._path_object.glob(pattern):
            for dirpath, dirnames, filenames in os.walk(self.path):

                for dirname in dirnames:

                    if not recursive and self._normalize_path(dirpath) != self.path:
                        break
                    
                    folder = os.path.join(dirpath, dirname)
                    folder = self._normalize_path(folder)
                        
                    if folder == self.path:
                        continue

                    current_depth = folder.count("/")

                    self.logger.info("Creating DirectoryObject for '{}' with depth: {}".format(
                        folder, current_depth))
                    dir_obj = self._this(folder, self.root_object)

                    yield dir_obj

        return generate_dir_objs()


if __name__ == "__main__":
    logging.basicConfig(level=0)
    do = DirectoryObject("../")
    for d in do.dirs:
        print(d.name, d.path, sep="; ")
    print("*"*10)
    for d in do.rdirs:
        print(d.name, d.path, sep="; ")
    pass
