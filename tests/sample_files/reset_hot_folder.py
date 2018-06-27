#!/usr/bin/env python3

""" This script deletes the sample package folders "foo" and "bar" if they exist. It then 
unzips the "hot_folder.zip" file so that unit tests and sample commands can be run again. """

# import modules.
import logging
import logging.config
import os
from shutil import rmtree
from zipfile import ZipFile


# enable logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# reset hot foler.
def reset():
    
    # set path to hot folder.
    here = os.path.dirname(__file__)
    hot_folder = os.path.join(here, "hot_folder.zip")
    hot_folder = os.path.abspath(hot_folder)

    # delete sample package folders.
    for folder in ["foo", "bar"]:
        folder = os.path.join(here, folder)
        folder = os.path.abspath(folder)
        try:
            logger.info("Deleting: {}".format(folder))
            rmtree(folder)
        except Exception as err:
            logger.warning("Can't delete: {}".format(folder))
            logger.error(err)

    # unzip file.
    with ZipFile(hot_folder) as zf:
        try:
            logger.info("Unzipping: {}".format(hot_folder))
            zf.extractall(here)
        except Exception as err:
            logger.warning("Can't unzip: {}".format(zfile))
            logger.error(err)

    return


if __name__ == "__main__":
    reset()