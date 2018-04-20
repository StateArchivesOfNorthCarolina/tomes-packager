""" ??? """


# import modules.
import os


class DirectoryObject(object):
    """ ??? """

    def __init__(self, path, name=None, files=[]):
        """ ??? name is an alias/nickname """

        # ???
        if not os.path.isdir(path):
            raise NotADirectoryError
        
        # ???
        self.path = path
        self.name = name
        self.files = files


if __name__ == "__main__":
    pass
