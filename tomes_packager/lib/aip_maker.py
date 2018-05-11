#!/usr/bin/env python3

""" This module contains a class for constructing the basic file and folder structure for a 
TOMES archival information package (AIP).

Todo:
    * Check in-line TODOs.
    * Vadlidate AIP after the fact - or during.?
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

    
    def __init__(self, account_id, source_dir, destination_dir):
        """ Sets instance attributes.

        Args:
            - account_id (str): ???
            - source_dir (str): ??? 
            - source_dir (str): ??? 

        Raises:
            - NotADirectoryError: If @source_dir or @destination_dir are not actual folder 
            paths.
        """

        # verify source_dir and destination_dir are folders.
        if not os.path.isdir(source_dir):
            msg = "Can't find source: {}".format(source_dir)
            raise NotADirectoryError(msg)
        if not os.path.isdir(destination_dir):
            msg = "Can't find destination: {}".format(destination_dir)
            raise NotADirectoryError(msg)

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.account_id = str(account_id) 
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        
        # convenience functions to join paths and normalize them.
        self._normalize_path = lambda p: os.path.abspath(p).replace("\\", "/")  
        self._join_paths = lambda *l: self._normalize_path(os.path.join(*l))
        
        # set source attributes.
        self.source_data = glob.glob(self._join_paths(self.source_dir, "**"), recursive=True)
        self.source_folders = [f for f in self.source_data if os.path.isdir(f)]
        self.source_files = [f for f in self.source_data if os.path.isfile(f)]
        self.source_eaxs = self._join_paths(self.source_dir, "eaxs", self.account_id)
        self.source_mime = self._join_paths(self.source_dir, "mime", self.account_id)
        self.source_pst = self._join_paths(self.source_dir, "pst")

        # set destination attributes.
        self.root = self._join_paths(self.destination_dir, self.account_id)
        self.metadata_dir = self._join_paths(self.root, "metadata")
        self.eaxs_dir = self._join_paths(self.root, "eaxs")
        self.mime_dir = self._join_paths(self.root, "mime")
        self.pst_dir = self._join_paths(self.root, "pst")
        self.metadata_dir = self._join_paths(self.root, "metadata")

        # ???
        self.transfers = {"attempted": [], "passed": [], "failed": []}
        self.is_valid = lambda: self.transfers["attempted"] == self.transfers["passed"]


    def _remove_folder(self, folder):
        """ ??? """

        # ???
        if len(os.listdir(folder)) != 0:
            self.logger.warning("Can't delete non-empty folder: {}".format(
                folder))
            return

        self.logger.info("Deleting folder: {}".format(folder))
        try:
            shutil.rmtree(folder)
        except Exception as err:
            # TODO: What exceptions?
            self.logger.warning("Can't delete source folder: {}".format(folder))
            self.logger.error(err)
            return
        
        return


    def _make_folder(self, folder):
        """ ???

        Args:
            - folder (str): The folder path to create.
        
        Returns:
            str: The return value.
            # ???
        
        Raises:
            - ???
        """

        # ???
        try:
            self.logger.info("Making folder: {}".format(folder))        
            os.mkdir(folder)
        except Exception as err:
            # TODO: What specific exceptions?
            self.logger.warning("Unable to create folder: {}".format(folder))
            self.logger.error(err)
            raise err

        return folder


    def _move_data(self, source_dir, destination_dir, is_files=True):
        """
        
        Args:
            - source_data (str): The directory path to ...
            - destiantion (str): The directory to which to move content in @source_data.
            - is_files (bool): Use True to move files???
        
        Returns:
           None
        """
        
        self.logger.info("Looking for candidate items in: {}".format(source_dir))

        # ???
        if is_files:
            data = [self._normalize_path(f) for f in self.source_files
                    if os.path.splitext(os.path.basename(f))[0] == self.account_id
                    and self._normalize_path(os.path.dirname(f)) == source_dir]
        else:
            data = [self._normalize_path(f) for f in self.source_folders
                    if self._normalize_path(os.path.dirname(f)) == source_dir]

        # ???
        if len(data) == 0:
            self.logger.warning("Unable to find any candidate items to move.")
            return
        else:
            self.transfers["attempted"] += data
            self.logger.info("Moving the following items: {}".format(data))
        
        # ???
        if not os.path.isdir(destination_dir):  
            self._make_folder(destination_dir)

        # ???
        for datum in data:
            try:
                self.logger.info("Moving '{}' to: {}".format(datum, destination_dir))
                shutil.move(datum, destination_dir)
                self.transfers["passed"].append(datum)
            except Exception as err:
                # TODO: What specific exceptions?
                self.logger.warning("Can't move '{}' to: {}".format(datum, destination_dir))
                self.logger.error(err)
                self.transfers["failed"].append(datum)
                # TODO: ???

        return

    def make_aip(self):
        """ ???

        Returns:
            None

        Raises:
            ValueError: If @self.root already exists.
        """

        # ???
        if os.path.isdir(self.root):
            msg = "AIP destination '{}' already exists; aborting.".format(self.root)
            self.logger.error(msg)
            raise ValueError(msg)
        else:
            self.logger.info("Creating AIP at: {}".format(self.root))

        # ???
        self._make_folder(self.root)        
        self._move_data(self.source_pst, self.pst_dir)
        self._move_data(self.source_eaxs, self.eaxs_dir, False)
        self._move_data(self.source_mime, self.mime_dir, False)

        # ???
        self._remove_folder(self.source_eaxs)
        self._remove_folder(self.source_mime)

        # ???
        metadata_files = [self._normalize_path(f) for f in self.source_files
                        if os.path.splitext(os.path.basename(f))[0] == self.account_id
                        and os.path.isfile(f)]
        if len(metadata_files) > 0:
            self.logger.info("Extra account files found.")
        
        # ???
        metadata_files = [os.path.dirname(f) for f in metadata_files]
        for metadata_file in metadata_files:
            self._move_data(metadata_file, self.metadata_dir)

        return


# TEST.
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    f = "../../tests/sample_files"
    am = AIPMaker("foo", f+"/hot_folder", f)
    am.make_aip()
    print(am.is_valid())
    am = AIPMaker("bar", f+"/hot_folder", f)
    am.make_aip()
    print(am.is_valid())
    

