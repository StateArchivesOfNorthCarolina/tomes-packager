#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import unittest
import logging
import tempfile
from datetime import datetime
from tomes_packager.lib.mets_maker import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_MetsMaker(unittest.TestCase):

    
    def setUp(self):

        # set attributes.
        self.sample_file = "sample_files/sample_mets_template.xml"


    def test__mets_validity(self):
        """ Is a rendered METS valid? """
        
        # make temporary file, save the filename, then delete the file.
        mets_handle, mets_path = tempfile.mkstemp(dir=".", suffix=".xml")
        os.close(mets_handle)
        os.remove(mets_path)

        # write a temporary METS file.
        self.mm = METSMaker(self.sample_file, mets_path,
                TIMESTAMP = lambda: datetime.now().isoformat() + "Z")
        self.mm.make()

        # see if METS is valid.
        self.assertTrue(self.mm.validate())
        os.remove(mets_path)


# CLI.
def main(template: "METS template file", output_file: "output METS XML file"):
    
    "Renders METS template with callable \"TIMESTAMP()\" variable to a METS XML file.\
    \nexample: `py -3 test__mets_maker.py sample_files/sample_mets_template.xml out.xml`"

    # create and self-validate METS file.
    mm = METSMaker(template, output_file, 
            TIMESTAMP = lambda: datetime.now().isoformat() + "Z")
    mm.make()
    mm.validate()


if __name__ == "__main__":

    import plac
    plac.call(main)
