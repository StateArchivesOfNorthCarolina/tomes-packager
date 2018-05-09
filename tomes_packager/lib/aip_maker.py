#!/usr/bin/env python3

""" This module contains a class for constructing the basic file and folder structure for a 
TOMES archival information package (AIP).

Todo:
    * @file_exclusions: going to actually us this?
    * Check in-line TODOs.
    * Need to move extraneous files to metadata/.
        - But how to identify extraneous? By basenames?
"""

# import modules.
import glob
import logging
import logging.config
import os
import shutil


class AIPMaker():
    """ A class for constructing the basic file and folder structure for a TOMES archival 
    information package (AIP). """

    
    def __init__(self, account_id, source_dir, destination_dir, file_exclusions=[]):
        """ Sets instance attributes.

        Args:
            - account_id (str): ???
            - source_dir (str): ??? 
            - source_dir (str): ??? 
            - file_exclusions (list): ???

        Raises:
            - NotADirectoryError: If @source_dir or @destination_dir are not actual folder 
            paths.
            - TypeError: If @files_exclusions is not a list.
        """

        # verify source_dir and destination_dir are folders.
        if not os.path.isdir(source_dir):
            msg = "Can't find source: {}".format(source_dir)
            raise NotADirectoryError(msg)
        if not os.path.isdir(destination_dir):
            msg = "Can't find destination: {}".format(destination_dir)
            raise NotADirectoryError(msg)

        # verify @files_exclusions is a list:
        if not isinstance(file_exclusions, list):
            msg = "Argument @file_exclusions must be a list; got: {}".format(
                    type(files_exclusions))
            raise TypeError(msg)
        
        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.account_id = str(account_id) 
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.file_exclusions = file_exclusions
        
        # convenience functions to join paths and normalize them.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")  
        self._join_paths = lambda *l: self._normalize_path(os.path.join(*l))
        
        # set additional attributes.
        self.data = glob.glob(self._join_paths(self.source_dir, "**"), recursive=True)
        self.folders = [f for f in self.data if os.path.isdir(f)]
        self.files = [f for f in self.data if os.path.isfile(f)]
        self.root = self._make_dir()
        self.metadata_dir = self._make_dir("metadata")
        self.eaxs_dir = self._make_dir("eaxs")
        self.mime_dir = self._make_dir("mime")
        self.pst_dir = self._make_dir("pst")

        # create AIP.
        self.make_aip()


    def _make_dir(self, subdir=None):
        """ ???

        Args:
            - subdir (str): ???
        
        Returns:
            str: The return value.
            # ???
        """
        
        # ???
        if subdir is None:
            folder = self._join_paths(self.destination_dir, self.account_id)        
        else:
            folder = self._join_paths(self.root, subdir)
        
        # ???
        try:
            self.logger.info("Making folder: {}".format(folder))        
            os.mkdir(folder)
        except Exception as err:
            self.logger.warning("Unable to create: {}".format(folder))
            self.logger.error(err)

        return folder


    def make_aip(self):
        """ ???

        Returns:
            ???
        """

        if self.root == "":
            self.logger.warning("Cannot add files to non-existant AIP folder; aborting.")
            return None
        
        # move optional PST file.
        pst_file = self.account_id + ".pst"
        psts = [os.path.abspath(f) for f in self.files if os.path.basename(f) == pst_file]
        
        if len(psts) == 0:
            self.logger.info("NO .pst file fount, removing: {}".format(self.pst_folder))
            os.rmdir(self.pst_folder)
            # TODO: OK, PST not required. ???
        else:
            pst = psts[0]
            try:
                shutil.move(pst, self.pst_dir)
            except Exception as err:
                # TODO: What specific exceptions?
                self.logger.warning("???: {}".format(pst))
                self.logger.error(err)
                # TODO: ???

        # move required EAXS files.
        source_eaxs = self._join_paths(self.source_dir, "eaxs", self.account_id)
        
        if not os.path.isdir(source_eaxs):
            self.logger.warning("???")
            self.logger.error("???")
            # TODO: raise something?
        else:
            try:
                shutil.move(source_eaxs, self.eaxs_dir)
            except Exception as err:
                # TODO: What specific exceptions?
                self.logger.warning("???: {}".format())
                self.logger.error(err)
                # TODO: ???
        
        # move MIME files.
        source_mime = self._join_paths(self.source_dir, "mime", self.account_id)
        if not os.path.isdir(source_mime):
            self.logger.warning("???")
            self.logger.error("???")
            # TODO: raise something?
        else:
            try:
                shutil.move(source_mime, self.mime_dir)
            except Exception as err:
                # TODO: What specific exceptions?
                self.logger.warning("???: {}".format())
                self.logger.error(err)
                # TODO: ???

        return


# TEST.
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    f = "../../tests/sample_files"
    am = AIPMaker("foo", f+"/hot_folder", f)
