#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import logging
import plac
import unittest
from tomes_packager.lib.premis_object import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_PREMISObject(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_file = "sample_files/sample_premis.log"
        self.events = PREMISObject.load_file(self.sample_file)
        self.premis = PREMISObject(self.events)


    def test__file_loader(self):
        """ Can @self.sample_file be loaded as a list? """
        
        self.assertTrue(isinstance(self.events, list))


    def test__required_attributes(self):
        """ Are the required attributes "entity" and "alias" present in @self.premis.agents, 
        @self.premis.events, and @self.premis.objects?  """
        
        # test for required attributes.
        tests = []
        for att in ["agents", "events", "objects"]:
            for item in getattr(self.premis, att):
                test_1 = hasattr(item, "entity")
                test_2 = hasattr(item, "name")
                tests += [test_1, test_2]

        # make sure False is not in @tests.
        self.assertTrue(False not in tests)


# CLI.
def main(premis_log:("PREMIS log file")):
    
    "Converts a PREMIS log file to a PREMISObject and prints the data to screen as JSON.\
    \nexample: `py -3 test__premis_object.py sample_files/sample_premis.log`"

    # convert @premis_log to a PREMISObject.
    events = PREMISObject.load_file(premis_log)
    premis = PREMISObject(events)
    
    # function to convert event data to JSON.
    js = lambda att: json.dumps([i.__dict__ for i in getattr(premis, att)], indent=2)

    # print event data.
    print("\nAgents: {}".format(js("agents")))
    print("\nEvents: {}".format(js("events")))
    print("\nObjects: {}".format(js("objects")))


if __name__ == "__main__":

    plac.call(main)