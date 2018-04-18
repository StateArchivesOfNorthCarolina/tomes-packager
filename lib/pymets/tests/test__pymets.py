#!/usr/bin/env python3

"""
Todo:
    * Add sample CLI command."
"""

# import modules.
import sys; sys.path.append("..")
import glob
import logging
import logging.config
import unittest
from pymets import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_PyMETS(unittest.TestCase):


    def setUp(self):

        self.pymets = PyMETS()


    def test__validation(self):
        """ Is the sample METS document valid? """

        # test if METS is valid
        sample = make_sample()
        is_valid = self.pymets.validate(sample)

        # check if result is as expected.
        self.assertEqual(True, is_valid)  


def make_sample(folder="."):
    """ Returns sample METS document as lxml.etree._Element. """

    # verify @folder is a directory.
    if not os.path.isdir(folder):
        msg = "Non-directory: {}; exiting.".format(folder)
        logging.error(msg)
        sys.exit(msg)

    # normalize @folder.
    folder = os.path.abspath(folder)

    # create PyMETS instance.
    pymets = PyMETS()

    # create METS root.
    root = pymets.make("mets")
    
    # create <metsHdr>; append to root.
    header = pymets.make("metsHdr")
    root.append(header)
    
    # create header <agent>.
    agent = pymets.make("agent", attributes={"ROLE":"CREATOR", "TYPE":"OTHER",
        "OTHERTYPE":"Software Agent"})
    header.append(agent)
    name = pymets.make("name")
    name.text = "PyMETS"
    agent.append(name)

    # create <fileSec>.
    fileSec = pymets.make("fileSec")
    root.append(fileSec) 
    fileGrp = pymets.fileGrp(filenames=glob.glob(folder + "/*.*"), basepath=None, 
            identifier="demo")
    fileSec.append(fileGrp)

    # create <structMap> and <div>.
    structMap = pymets.make("structMap")
    root.append(structMap)
    file_ids = pymets.get_fileIDs(fileSec)
    div = pymets.div(file_ids)
    structMap.append(div)
    
    # add comment.
    msg = "It is {} that this METS file is valid per {}.".format(pymets.validate(root), 
            pymets.xsd_file)
    root.append(pymets.Comment(msg))
    
    # return string version of @root.
    root = pymets.stringify(root)
    return root


# CLI TEST.
def main(folder:("???")="."):
    
    "Prints METS file based on current directory."

    # get sample; print to string.
    mets = make_sample(folder)
    print(mets)


if __name__ == "__main__":

    import plac
    plac.call(main)

