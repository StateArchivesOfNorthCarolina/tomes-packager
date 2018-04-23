""" ???

Todo:
    * Too much normalize path everywhere.
    * Use folders instead of "dirs"
    * Can search/find/names be recursive?
        - Should depend on dirs vs rdirs.
    * .name is still not relative to master_object root???
        - also: change name to "relname"??? NO.
        - name needs to call a function and be relative to the container dir's name using parent object?
        >>> par = d.dirs[0].dirs[1].parent_object.path
        >>> kid = d.dirs[0].dirs[1].path
        >>> os.path.relpath(kid, par)
    * ListObject:
        - names() should just call a function so to avoid parens.
        - add basenames() too.
    * Add ctime/mtime.
    * Make get_id a method; too complex for lambda.
        - Use depth as a padded leading decimal number for the index: e.g. 01.001
        - No, just get rid of it now that index is an int.
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

# I still want a way to call a folder don't I? Maybe better query options.
##        def __getattr__(self, attr):
##            """ ??? Get rid of this: it's dangerous if there's a name conflict.
##            i.e. folder called "find" or "search".
##            AND it's not recursive. """
##            
##            try:
##                names = [d.name for d in self]
##                found = names.index(attr)
##                folder_object = self[found]
##                return folder_object
##            except ValueError as err:
##                msg = "Attribute '{}' does not exist.".format(attr)
##                raise AttributeError(msg)


        def __contains__(self, test):
            """ ??? """

            r = False
            if self.find(test) is not None:
                r = True
            return r


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

            # catch: sre_constants.error
            r = []
            for d in self:
                t = re.search(term, d.name)
                if t is not None:
                    r.append(self.index(d))
            return r


        def names(self, indexes=None):

            if indexes == None:
                indexes = range(0, len(self) + 1)
            n = [d.name for d in self if self.index(d) in indexes]
            if len(n) == 0:
                n = None
            return n

        def basenames(self, indexes=None):

            if indexes == None:
                indexes = range(0, len(self) + 1)
            n = [d.basename for d in self if self.index(d) in indexes]
            if len(n) == 0:
                n = None
            return n

        
    @classmethod
    def this(cls, *args):
        return cls(*args)
    
        
    def __init__(self, path, master_object=None, parent_object=None, depth=0):
        """ ??? """

        # ???
        if not os.path.isdir(path):
            raise NotADirectoryError
        self.isdir = True
        self.isfile = False
        normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")

        # ???
        self.path = normalize_path(path)
        self.parent_object = parent_object
        self.depth = depth
        self.index = 0
        self.abspath = normalize_path(os.path.abspath(path))
        self.file_object = FileObject

        # ???
        self.dirs = self.__ListObject()
        self.rdirs = self.__ListObject()
        self.files = self.__ListObject()
        self.rfiles = self.__ListObject()
        
        # ???
        def get_master_object():
            if master_object is None:
                #self.index += 1
                return self
            else:
                #master_object.index += 1
                return master_object
        self.master_object = get_master_object()
            
        # ???
        def get_parent():
            if self.parent_object is not None:
                return self.parent_object.basename
        self.parent = get_parent()

        # ???
        self.basename = os.path.basename(self.path)

        # ???
        def get_name():
            if self.depth > 0:
                n = os.path.relpath(self.path, self.master_object.path)
                return normalize_path(n)
            else:
                return ""
        self.name = get_name()

        # ???
        get_pad_len = lambda x: 1 + len(str(x))
        def get_id(i, files_len):
            #ipad = get_pad_len(files_len)
            #i = str(i).zfill(ipad)
            #return "{}.{}.{}".format(self.index, self.depth, i)
            #return "{}.{}".format(self.index, i)
            return i

        files = [normalize_path(f) for f in glob.glob(self.path + "/*.*") if os.path.isfile(f)]
        if self.parent_object is None:
            i = self
        else:
            i = self.master_object
        files_len = len(files)
        for f in files:
            f = self.file_object(f, self, master_object=self.master_object, index=get_id(i.index, files_len))
            self.files.append(f)
            i.index += 1
            
        # ???
        folders = [normalize_path(f) for f in glob.glob(self.path + "/*/")]
        for folder in folders:
            folder = self.this(os.path.abspath(folder), self.master_object, self, self.depth+1)
            self.dirs.append(folder)
                    
        # ???
        def get_recur(do, lo, mstr=None, att="dirs" ):
            if mstr is None:
                    mstr = do
            if hasattr(do, att):
                    lo += getattr(do, att)
                    for f in do.dirs:
                            get_recur(f, lo, mstr, att)
            return lo

        self.rdirs = get_recur(self, self.rdirs)
        self.rfiles = get_recur(self, self.rfiles, att="files")


if __name__ == "__main__":
    d = DirectoryObject("C:/Users/Nitin/Dropbox/TOMES/GitHub/tomes_packager/")
    #d = DirectoryObject(".")

