#!/usr/bin/env python3

""" This module contains a class for creating a read-only object representation of a folder.
"""

# import modules.
import logging
import logging.config
import os
from datetime import datetime
from .file_object import FileObject


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
        - dirs (function): Returns a generator for all subfolders (non-recursive) within 
        @self.path. Each item is a DirectoryObject.
        - rdirs (function):  Returns a generator for all subfolders (recursive) within 
        @self.path. Each item is a DirectoryObject.
        - files (function): Returns a generator for all files (non-recursive) within 
        @self.path. Each item is a FileObject.
        - rfiles (function): Returns a generator for all files (recursive) within @self.path.
        Each item is a FileObject.
    """


    def __init__(self, path, parent_object=None, root_object=None, depth=0):
        """ Sets instance attributes.
        
        Args:
            - path (str): A path to an actual folder.
            - parent_object (DirectoryObject): The parent folder to which @path belongs.
            - root_object (DirectoryObject): The root or "master" folder under which the @path
            folder and its @parent_object reside.
            - depth (int): ???

        Raises:
            - NotADirectoryError: If @path is not an actual folder path.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience function to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")  
        
        # normalize @path and log status.
        path = self._normalize_path(path)
        if root_object is None:
            self.logger.info("Initializing DirectoryObject for: {}".format(path))            
        else:
            self.logger.debug("Initializing DirectoryObject for: {}".format(path))            

        # verify @path is a folder.
        if not os.path.isdir(path):
            msg = "Can't find: {}".format(path)
            self.logger.error(msg)
            raise NotADirectoryError(msg)

        # set attributes.
        self.path = path
        self.parent_object = parent_object
        self.root_object = self if root_object is None else root_object
        self.depth = depth

        # set path attributes.
        self.isdir = True
        self.isfile = False
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

        # create attributes for directory and file objects.
        self.dirs = lambda: self._get_dirs()
        self.rdirs = lambda: self._get_dirs(True)
        self.files = lambda: self._get_files()
        self.rfiles = lambda: self._get_files(True)

    
    @classmethod
    def _this(cls, *args, **kwargs):
        """ Returns instance of this class. """

        return cls(*args, **kwargs)


    def _get_files(self, recursive=False):
        """ Yields a FileObject for every file in @self.path.

        Args:
            - recursive (bool): Use True to include FileObjects in subfolders. Use False to 
            omit subfolders.

        Returns:
            generator: The return value.
        """

        self.logger.debug("Creating FileObject(s) in: {}".format(self.path))
  
        # iterate through folders and yield FileObject(s).
        def gen_files():

            # track file positions.
            file_pos = 0
            
            for dirpath, dirnames, filenames in os.walk(self.path):

                for filename in filenames:

                    # if @recursive is False, don't go into subfolders.
                    if not recursive and self._normalize_path(dirpath) != self.path:
                        break
                    
                    # get file path.
                    filepath = os.path.join(dirpath, filename)
                    filepath = self._normalize_path(filepath)

                    # build DirectoryObject for parent folder of @filepath.
                    parent_obj = self._this(path=os.path.dirname(filepath), 
                            parent_object=dirpath, root_object=self.root_object)
                    
                    # build FileObject for @filepath.
                    file_obj = self._file_object(path=filepath, 
                            parent_object=parent_obj, root_object=self.root_object, 
                            index=file_pos)

                    yield file_obj
                    file_pos += 1

        return gen_files()

    
    def _get_dirs(self, recursive=False):
        """ Yields a DirectoryObject for every folder in @self.path.

        Args:
            - recursive (bool): Use True to include DirectoryObjects in subfolders. Use False
            to omit subfolders.

        Returns:
            generator: The return value.
        """

        self.logger.debug("Creating DirectoryObject(s) in: {}".format(self.path))
  
        # iterate through folders and yield DirectoryObject(s).
        def gen_dirs():
  
            for dirpath, dirnames, filenames in os.walk(self.path):
                
                # sort folders per: https://stackoverflow.com/a/6670926.
                dirnames.sort()
                
                for dirname in dirnames:

                    # if @recursive is False, don't go into subfolders.
                    if not recursive and self._normalize_path(dirpath) != self.path:
                        break
                    
                    # get folder path.
                    folder = os.path.join(dirpath, dirname)
                    folder = self._normalize_path(folder)
                        
                    # if @folder is @self.path, skip it.
                    if folder == self.path:
                        continue
 
                    # build DirectoryObject for parent folder of @folder.
                    parent_obj = self._this(path=os.path.dirname(folder), 
                            parent_object=dirpath, root_object=self.root_object, 
                            depth = self.depth - 1)
                    
                    # build DirectoryObject for @folder.
                    dir_obj = self._this(path=folder, parent_object=parent_obj, 
                            root_object=self.root_object, depth = self.depth + 1)

                    yield dir_obj

        return gen_dirs()
    

    def graph(self):
        """ Creates a visual tree representation of @self.path.
            
        Returns:
            generator: The return value.
            Each item is a line in the graph.
        """
        
        self.logger.info("Creating graph of: {}".format(self.path))

        # iterate through files and folders to create graph lines.
        def grapher(path=self):

            line = ("|  " * path.depth) + path.basename + "/"
            yield line
            for fil in path.files():
                line = ("|  " * path.depth) + "|  " + fil.basename
                yield line
            for folder in path.dirs():
                for line in grapher(folder):
                    yield line

        return grapher()


if __name__ == "__main__":
    pass
