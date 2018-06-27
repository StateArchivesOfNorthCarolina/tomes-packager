#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import plac
import unittest
from lxml import etree
from tomes_packager.lib.rdf_maker import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_RDFMaker(unittest.TestCase):

    
    def setUp(self):

        # set attributes.
        self.sample_file = "sample_files/sample_rdf.xlsx"
        self.rm = RDFMaker(self.sample_file)
        self.rm.make()

    
    def test__rdf_count(self):
        """ Do exactly two RDF documents get created from the sample file? """

        total_rdfs = len(self.rm.rdfs)
        self.assertTrue(total_rdfs == 2)


    def test__rdf_validity(self):
        """ Is the first RDF in @self.rm valid? """
        
        # only valid RDFs should be stored to an RDFMaker object - so this is redundant.
        xml = self.rm.rdfs[0].xml
        self.assertTrue(self.rm.validate(xml))


# CLI.
def main(rdf_xlsx: "RDF/Dublin Core .xlsx file"):
    
    "Converts an RDF/Dublin Core .xlsx file to XML and prints it to screen.\
    \nexample: `py -3 test__rdf_maker.py sample_files/sample_rdf.xlsx`"
	
    # create root XML element.
    root = etree.Element("root")

    # create the RDF object and append all etree._Element's to @root.
    rm = RDFMaker(rdf_xlsx)
    rm.make()
    for rdf in rm.rdfs:
        root.append(rdf.element)

    # write @root to @output_file.
    utf8 = "utf-8"
    xstring = etree.tostring(root, xml_declaration=True, encoding=utf8, 
            pretty_print=True).decode(utf8)
    print(xstring)


if __name__ == "__main__":

    plac.call(main)
