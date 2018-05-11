#!/usr/bin/env python3

""" This module contains a class for constructing the basic file and folder structure for a 
TOMES archival information package (AIP).

Todo:
    * @file_exclusions: going to actually us this?
    * Check in-line TODOs.
    * Need to move extraneous files to metadata/.
        - But how to identify extraneous? By basenames?
    * Have a cleanup function to clean up the hot folder.
    * Make a general purpose file mover function AND one for folders.
    * Vadlidate AIP after the fact - or during.
    * ABORT if destination folder already exists.
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
            self.logger.warning("Unable to create: {}".format(folder))
            self.logger.error(err)
            raise err

        return folder


    def _move_data(self, data, destination_dir, is_files=True):
        """
        
        Args:
            - data (list):
            - destiantion (str):
            - is_files (bool): Use True if @data is a list of files. If it is a list of 
            folders, use False.
        
        Returns:
            tuple: The return value.
            The first item is a list of items that were successfully moved to @parent_dir.
            The second item is the list of items that were not moved.
        """
        
        # ???
        if is_files:
            data = [self._normalize_path(f) for f in self.source_files
                    if os.path.splitext(os.path.basename(f))[0] == self.account_id
                    and self._normalize_path(os.path.dirname(f)) in data]
        else:
            data = [self._normalize_path(f) for f in self.source_folders
                    if self._normalize_path(os.path.dirname(f)) in data]

        # ???
        if len(data) == 0:
            self.logger.warning("Unable to find data requested for moving; skipping.")
            return

        # ???
        if not os.path.isdir(destination_dir):  
            self._make_folder(destination_dir)

        # ???
        for datum in data:
            try:
                if is_files:
                    msg = "Moving file '{}' to: {}".format(datum, destination_dir)
                else:
                    msg = "Moving files and sobfolders in '{}' to: {}".format(datum, 
                            destination_dir)
                self.logger(msg)
                shutil.move(datum, destination_dir)
            except Exception as err:
                # TODO: What specific exceptions?
                self.logger.warning("Can't move '{}' to: {}".format(datum, destination_dir))
                self.logger.error(err)
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
            msg = "Destination '{}' already exists.".format(self.root)
            self.logger.error(msg)
            raise ValueError(msg)
                
        # ???
        self._make_folder(self.root)        
        self._move_data([self.source_pst], self.pst_dir)
        self._move_data([self.source_eaxs], self.eaxs_dir, False)
        self._move_data([self.source_mime], self.mime_dir, False)

        return


# TEST.
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    f = "../../tests/sample_files"
    am = AIPMaker("foo", f+"/hot_folder", f)
    am.make_aip()
    am = AIPMaker("bar", f+"/hot_folder", f)
    am.make_aip()

