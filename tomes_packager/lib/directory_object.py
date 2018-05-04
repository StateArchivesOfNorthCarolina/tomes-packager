#!/usr/bin/env python3

""" This module contains a class for creating a read-only object representation of a folder. 
"""

# import modules.
import sys; sys.path.append("..")
import glob
import logging
import logging.config
import os
from datetime import datetime
from lib.directory_object_lib.file_object import FileObject
from lib.directory_object_lib.list_object import ListObject


class DirectoryObject(object):
    """ A class for creating a read-only object representation of a folder. """


    def __init__(self, path, parent_object=None, root_object=None, depth=0):
        """ Sets instance attributes.
        
        Args:
            - path (str): A path to an actual folder.
            - parent_object (DirectoryObject): The parent folder to which the @path file 
            belongs.
            - root_object (DirectoryObject): The root or "master" folder under which the @path
            folder and its @parent_object reside.
            - depth (int): The subfolder depth from @path to the @root_object.

        Raises:
            NotADirectoryError: If @path is not an actual folder path.
        """

        # verify @self.path is a folder.
        if not os.path.isdir(path):
            raise NotADirectoryError
        self.isdir = True
        self.isfile = False

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience function to clean up path notation.
        self.normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")  

        # set attributes.
        self.path = self.normalize_path(path)
        self.parent_object = parent_object
        self.root_object = self if root_object is None else root_object
        self.depth = depth
        
        # set path attributes.
        self.name = self.normalize_path(os.path.relpath(self.path, 
            start=self.root_object.path)) 
        self.basename = os.path.basename(self.path)
        self.abspath = self.normalize_path(os.path.abspath(self.path))

        # set folder metadata.
        iso_date = lambda t: datetime.utcfromtimestamp(t).isoformat() + "Z"
        self.created = iso_date(os.path.getctime(path))
        self.modified = iso_date(os.path.getmtime(path))

        # start counter for file indices.
        self._file_index = 0

        # add dependency attributes.
        self._file_object = FileObject
        self._list_object = ListObject

        # create ListObjects for non-recursive and recursive files and folders.
        self.dirs, self.files = self._get_dirs_files()
        self.rdirs = self._get_recursive_object(self, self._list_object())
        self.rfiles = self._get_recursive_object(self, self._list_object(), attr="files")

    
    @classmethod
    def _this(cls, *args, **kwargs):
        """ Returns instance of this class. """

        return cls(*args, **kwargs)


    def _get_dirs_files(self):
        """ Creates DirectoryObject and FolderObject instances for each folder and file in the
        @self directory.

        Returns:
            tuple: The return value.
            The first item is a ListObject of DirectoryObject instances - the folders within 
            self.
            The second item is a ListObject of FileObject instances - the files within self.
            Note, each DirectoryObject instance will itself contain a ListObject instances of
            both its folders and files as DirectoryObject and FileObject instances.
        """
        
        # determine the root object of @self.
        if self.parent_object is None:
            obj = self
        else:
            obj = self.root_object

        # glob @self for its files.
        self.logger.info("Globbing files in: {}".format(self.path))
        files = [self.normalize_path(f) for f in glob.glob(self.path + "/*.*") 
                if os.path.isfile(f)]
        files_len = len(files)
        self.logger.info("Files found: {}".format(files_len))

        # create a ListObject and append each file to it as FileObject instances.
        file_objects = self._list_object()
        for fil in files:
            self.logger.debug("Creating FileObject for '{}' with index: {}".format(fil, 
                obj._file_index))
            fil = self._file_object(fil, self, root_object=self.root_object, 
                    index=obj._file_index)
            file_objects.append(fil)
            obj._file_index += 1
            
        # glob @self for its folders.
        self.logger.info("Globbing folders in: {}".format(self.path))
        folders = [self.normalize_path(f) for f in glob.glob(self.path + "/*/") 
                if os.path.isdir(f)]
        self.logger.info("Folders found: {}".format(len(folders)))

        # create a ListObject and append each folder to it as DirectoryObject instances.
        dir_objects = self._list_object()
        for folder in folders:
            current_depth = self.depth + 1
            self.logger.debug("Creating DirectoryObject for '{}' with depth: {}".format(
                folder, current_depth))     
            folder = self._this(os.path.abspath(folder), parent_object=self, 
                    root_object=self.root_object, depth=current_depth)
            dir_objects.append(folder)

        return (dir_objects, file_objects)

            
    def _get_recursive_object(self, dir_obj, list_obj, master_obj=None, attr="dirs" ):
        """ Creates a ListObject of all (i.e. recursive) DirectoryObject or FileObject 
        instances within @self.

        Args:
            - dir_obj (DirectoryObject): The DirectoryObject with which to get recursive 
            folder and file objects. 
            - list_obj (ListObject): The ListObject instance in which to append each folder or
            files object.
            - master_obj (DirectoryObject): The root object under which the directory @self
            exists.
            - attr (str): Use either "dirs" or "files" to obtains recursive DirectoryObject or
            FileObject instances, respectively.
        
        Returns:
            ListObject: The return value.

        Raises:
            ValueError: If @attr is not "dirs" or "files".
        """

        # verify @attr is legal.
        legal_attrs =  ["dirs", "files"]
        if attr not in legal_attrs:
            err = "Illegal 'attr' argument '{}'; must be one of: {}".format(attr, legal_attrs)
            self.logger.error(err)
            raise ValueError(err)
        
        # determine the root or "master" object.
        if master_obj is None:
            master_obj = dir_obj
            
        # if @dir_obj has the attribute @attr, append the attribiute value to @list_obj and 
        # run this method on @dir_obj's own folders - thereby appending those folders to
        # @list_obj.
        if hasattr(dir_obj, attr):
            list_obj += getattr(dir_obj, attr)
            for d in dir_obj.dirs:
                self._get_recursive_object(d, list_obj, master_obj, attr)
        
        recursive_obj = list_obj
        return recursive_obj


if __name__ == "__main__":
    pass