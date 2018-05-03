#!/usr/bin/env python3

""" This module contains a class for ...

Todo:
    * Can search/find/names be recursive?
        - Should depend on dirs vs rdirs.
    * .name is still not relative to root_object root???
        - also: change name to "relname"??? NO.
        - name needs to call a function and be relative to the container dir's name using parent object?
        >>> par = d.dirs[0].dirs[1].parent_object.path
        >>> kid = d.dirs[0].dirs[1].path
        >>> os.path.relpath(kid, par)
    * Add ctime/mtime.
    * Go back to calling this DirectoryObject!! :-]
"""

# import modules.
import sys; sys.path.append("..")
import glob
import logging
import logging.config
import os
from lib.folder_object_lib.file_object import FileObject
from lib.folder_object_lib.list_object import ListObject


class FolderObject(object):
    """ A class for ... """


    def __init__(self, path, parent_object=None, root_object=None, depth=0):
        """ Sets instance attributes.
        
        Args:
            - path (str):
            - parent_object (FolderObject): The parent folder to which the @path file belongs.
            - root_object (FolderObject): The root or "master" FolderObject under which the 
            @path file and its @parent_object reside.
            - depth (int):

        Raises:
            NotADirectoryError: If @path is not an actual folder path.
        """

        # verify @self.path is a folder.
        if not os.path.isdir(path):
            raise NotADirectoryError
        self.isdir = True
        self.isfile = False

        # convenience function to clean up path notation.
        self.normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")  

        # set attributes.
        self.path = self.normalize_path(path)
        self.parent_object = parent_object
        self.root_object = self if root_object is None else root_object
        self.depth = depth
        
        # set path attributes.
        self.name = ""
        if self.depth > 0:
            self.name = self.normalize_path(os.path.relpath(self.path, 
                start=self.root_object.path)) 
        self.basename = os.path.basename(self.path)
        self.abspath = self.normalize_path(os.path.abspath(self.path))

        # start counter for file indices.
        self._file_index = 0

        # add dependency attributes.
        self.file_object = FileObject
        self.list_object = ListObject

        # create ListObjects for non-recursive and recursive files and folders.
        self.dirs, self.files = self.__get_assets()
        self.rdirs = self.__get_recursives(self, self.list_object())
        self.rfiles = self.__get_recursives(self, self.list_object(), attr="files")

    
    @classmethod
    def this(cls, *args, **kwargs):
        """ Returns instance of this class. """

        return cls(*args, **kwargs)


    def __get_assets(self):
        """ """
        
        # ???
        if self.parent_object is None:
            obj = self
        else:
            obj = self.root_object

        # ???
        files = [self.normalize_path(f) for f in glob.glob(self.path + "/*.*") 
                if os.path.isfile(f)]
        files_len = len(files)

        # ???
        file_objects = self.list_object()
        for fil in files:
            fil = self.file_object(fil, self, root_object=self.root_object, 
                    index=obj._file_index)
            file_objects.append(fil)
            obj._file_index += 1
            
        # ???
        folders = [self.normalize_path(f) for f in glob.glob(self.path + "/*/")]

        dir_objects = self.list_object()
        for folder in folders:
            folder = self.this(os.path.abspath(folder), parent_object=self, 
                    root_object=self.root_object, depth=self.depth+1)
            dir_objects.append(folder)

        return dir_objects, file_objects

            
    def __get_recursives(self, dir_obj, list_obj, master_obj=None, attr="dirs" ):
        """ ??? """

        if master_obj is None:
            master_obj = dir_obj
        if hasattr(dir_obj, attr):
            list_obj += getattr(dir_obj, attr)
            for d in dir_obj.dirs:
                self.__get_recursives(d, list_obj, master_obj, attr)
        
        return list_obj


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    f = FolderObject("C:/Users/Nitin/Dropbox/TOMES/GitHub/tomes_packager/")
    #d = DirectoryObject(".")
    print(f.dirs)



