""" ???

Todo:
    * Too much normalize path.
    * need "alias" optional arg for .name of ROOT.
    * can search/find/names be recursive?
    * Think self.path MUST be absolute, so force that.
        - No. Is ok.
    * .name is still not relative to master root???
    * File indexes in files are using rfiles as basis.
        - Use the count of slashes as a padded leading decimal number for the index.
            - e.g. 01.001
"""


# import modules.
import sys; sys.path.append("..")
import glob
import os
import re
from lib.file_object import FileObject


class DirectoryObject(object):
    """ ??? """

    class __ListObject(list):
        """ ??? """
        
        def __getattr__(self, attr):
            """ ??? Get rid of this: it's dangerous if there's a name conflict. """
            
            try:
                names = [d.name for d in self]
                found = names.index(attr)
                folder_object = self[found]
                return folder_object
            except ValueError as err:
                msg = "Attribute '{}' does not exist.".format(attr)
                raise AttributeError(msg)

        def __contains__(self, test):
            """ ??? """

            # ???
            return True if self.find(test) is not None else False


        def find(self, term):
            """ ??? """

            r = None
            for d in self:
                if d.name == term:
                    r = self.index(d)
                    break
            return r

            
        def search(self, term):
            """ ??? """

            # sre_constants.error

            # ???
            r = []
            for d in self:
                t = re.search(term, d.name)
                if t is not None:
                    r.append(self.index(d))
            return r


        def names(self, indexes=None):

            if indexes == None:
                indexes = range(0, len(self) + 1)
            #if not self.recursive:
            n = [d.name for d in self if self.index(d) in indexes]
            #else:
            #    n = [d.parent + "/" + d.name for d in self if self.index(d) in indexes]
            if len(n) == 0:
                n = None
            return n

        
    @classmethod
    def this(cls, p):
        return cls(p)
    
        
    def __init__(self, path):
        """ ??? name is an alias/nickname """

        # ???
        if not os.path.isdir(path):
            raise NotADirectoryError
        self.isdir = True
        self.isfile = False
        normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")

        # ???
        self.path = normalize_path(path)
        self.abspath = normalize_path(os.path.abspath(path))
        self.file_object = FileObject
        self.parent = os.path.split(self.path)[0]

        # ???
        self.name = os.path.basename(self.path)
        #self.lname = os.path.relpath(self.parent, self.path) # how to get relpath?
        """ os.path.relpath(d.dirs[0].dirs[0].path, d.path)
        >>> os.path.relpath(d.dirs[0].dirs[1].dirs[0].path, d.path)
        'lib\\__pycache__\\foo'
        You prolly need to wrap this class in another in ordeer to preserve the root path? Fuck. """

        # ???
        self.dirs = self.__ListObject()
        self.files = self.__ListObject()
        self.rfiles = self.__ListObject()

        # get padding length for local file identifiers
        # TODO make get_id a method; too comlex for lambda.
        get_pad_len = lambda x: 1 + len(str(len(x)))
        get_id = lambda file, files: str(files.index(file)).zfill(get_pad_len(files))

        # root folder dirs.
        folders = [normalize_path(f) for f in glob.glob(self.path + "/*/")]
        for folder in folders:
            par = os.path.split(folder)[0]
            folder = self.this(folder)
            self.dirs.append(folder)

        # root folder files. TODO indexes not unique?
        files = [normalize_path(f) for f in glob.glob(self.path + "/**", recursive=True)
                 if os.path.isfile(f)]
        files = [self.file_object(f, self, index=get_id(f, files), parent=self.path) for f in files]
        for f in files:
            self.rfiles.append(f)
            if f.name.count("/") == 0:
                self.files.append(f)
        
        # subfolder files.
        for folder in self.dirs:
            files = [normalize_path(f) for f in glob.glob(folder.path + "/**", recursive=True)
                 if os.path.isfile(f)]
            files = [self.file_object(f, folder, index=get_id(f, files), parent=folder.path) for f in files]
            folder.rfiles = self.__ListObject() # avoids redundance.
            for f in files:
                folder.rfiles.append(f)
                if f.name.count("/") == 0:
                    folder.files.append(f)

if __name__ == "__main__":
    #d = DirectoryObject("C:/Users/Nitin/Dropbox/TOMES/GitHub/tomes_packager/tomes_packager")
    d = DirectoryObject("../..")


    
