#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import os
import random
import shutil
import unittest
from zipfile import ZipFile
from tomes_packager.lib.aip_maker import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


# set variables.
ACCOUNTS = ["foo", "bar"]
SAMPLE_FOLDER = "sample_files"
HOT_FILE = os.path.join(SAMPLE_FOLDER, "hot_folder.zip")
HOT_FOLDER = os.path.join(SAMPLE_FOLDER, "hot_folder")

# deletes a folder and re-unzips @HOT_FILE into @SAMPLE_FOLDER.
def cleanup(folder):

    # remove @folder.
    try:
        shutil.rmtree(folder)
    except Exception as err:
        logging.warning("Can't delete test folder: {}".format(folder))
        logging.error(err)

    # unzip @HOT_FILE to @SAMPLE_FOLDER.
    logging.info("Deleting AIP: {}".format(folder))
    with ZipFile(HOT_FILE) as zf:
        try:
            zf.extractall(SAMPLE_FOLDER)
        except Exception as err:
            logging.warning("Can't unzip: {}".format(HOT_FILE))
            logging.error(err)
    
    return


class Test_AIPMaker(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_folder = SAMPLE_FOLDER
        self.hot_file = HOT_FILE
        self.hot_folder = HOT_FOLDER
        self.accounts = ACCOUNTS
        self.cleanup = cleanup


    def test__aip_validity(self):
        """ Is a rendered AIP valid? """
        
        # pick a ranndom account.
        account = random.choice(self.accounts)

        # make the AIP.
        am = AIPMaker(account, self.hot_folder, self.sample_folder)    
        am.make()

        # see if AIP is valid.
        self.assertTrue(am.validate())
        self.cleanup(am.root)


# CLI.
def main(account_id:("email account identifier", "positional", None, str, ACCOUNTS), 
        delete_aip:("delete the AIP and reset sample_files/hot_folder", "flag", "d")=False):
    
    "Creates AIP folder from data in source directory \"sample_files/hot_folder\".\
    \nexample: `py -3 test__aip_maker.py foo`"

    # create and self-validate an AIP.
    try:
        am = AIPMaker(account_id, "sample_files/hot_folder", "sample_files/")    
        am.make()
        is_valid = am.validate()
    except Exception as err:
        is_valid = False
        logging.warning("Can't make AIP for: {}".format(account_id))
        logging.error(err)

    # if needed, run @cleanup().
    if delete_aip:
        cleanup(am.root)

    # print if the AIP is/was valid.
    if is_valid:
        print("AIP is valid.")
    else:
        print("AIP is not valid.")


if __name__ == "__main__":

    import plac
    plac.call(main)
