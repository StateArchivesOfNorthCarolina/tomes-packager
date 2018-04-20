""" ??? """


# import modules.
import os


class DirectoryToObject(object):
    """ ??? """

    def __init__(self, path, name=None, files=[]):
        """ ??? name is an alias/nickname """
        
        # ???
        self.path = path
        self.name = name
        self.files = files

        # ???
        if not os.path.isdir(self.path):
            raise NotADirectoryError


if __name__ == "__main__":
    pass
