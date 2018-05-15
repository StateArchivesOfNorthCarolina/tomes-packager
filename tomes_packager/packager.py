""" This module contains a class for constructing a TOMES archival information package (AIP)
with an optional METS file.

Todo:
    * Need to determine constant vars.
        - ISO/UTC now (aka @timestamp).
        - What else?
    * If AIP restructing works but METS fails, we need a function to JUST
    drop in the METS (and to create DirectoryObject) - also useful if AIP 
    already exists.
        - Can't you just using METSMaker for that now?
"""

# import modules.
import jinja2
import logging
import logging.config
import os
from datetime import datetime
from lxml import etree
from lib.aip_maker import AIPMaker
from lib.directory_object import DirectoryObject
from lib.events_object import EventsObject
from lib.mets_maker import METSMaker
from lib.rdf_maker import RDFMaker

    
class Packager():
    """ A class for constructing a TOMES archival information package (AIP) with an optional 
    METS file. """


    def __init__(self, account_id, source_dir, destination_dir, mets_template="", 
            preservation_events={}, rdf_xlsx="", charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            - account_id (str): The email account's base identifier, i.e. the file prefix.
            - source_dir (str): The folder path from which to transfer data.
            - destination_dir (str): The folder path in which to create the AIP structure.
            - mets_template (str): The file path for the METS template. This will be used to
            render a METS file inside the AIP's root folder. For more information, see: 
            "https://github.com/StateArchivesOfNorthCarolina/tomes-packager/blob/master/docs/documentation.md".
            - preservation_events (dict): Optional preservation events to pass into 
            @mets_template.
            - rdf_xlsx (str): The Excel 2010+ (.xlsx) file from which to create RDFs. 
            - charset (str): The encoding for the rendered METS an RDF data.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience functions to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")
        self._abspath = lambda p: self._normalize_path(os.path.abspath(p))

        # set attributes.
        self.account_id = str(account_id) 
        self.source_dir = self._normalize_path(source_dir)
        self.destination_dir = self._normalize_path(destination_dir)
        self.preservation_events = EventsObject(preservation_events)
        self.mets_template = mets_template
        self.rdf_xlsx = rdf_xlsx
        self.charset = charset

        # set attributes for imported classes.
        self._aip_maker = AIPMaker
        self._directory_object = DirectoryObject
        self._mets_maker = METSMaker
        self._rdf_maker = RDFMaker

        # creates atttibutes for calculated objects.
        self.aip = None
        self.directory = None
        self.mets = None
        self.rdf = None


    def package(self):
        """ Creates the AIP structure and optional METS file.
        
        Returns:
            tuple: The return value.
            The first item is he AIP folder's absolute path. The second item is the METS 
            file's base name (None if no METS was created). The third item is a boolean:
            False if the AIP structure and/or the METS is invalid and/or the METS template
            failed to render (likely due to user error). Otherwise, True.
        """

        # set AIP path.
        aip_dir = self._abspath(os.path.join(self.destination_dir, self.account_id))
        self.logger.info("Packaging: {}".format(aip_dir))

        # create AIP structure.
        self.aip = self._aip_maker(self.account_id, self.source_dir, self.destination_dir)
        self.aip.make()

        # if the AIP structure isn't valid, warn but continue on.
        if not self.aip.validate():
            self.logger.warning("AIP structure is invalid; continuing anyway.")

        # if no METS template was passed; return AIP.
        if self.mets_template == "":
            self.logger.info("No METS template passed; skipping METS creation.")
            return (aip_dir, None, self.aip.validate())

        # create a DirectoryObject for the AIP.
        self.directory = self._directory_object(aip_dir)

        # if needed, create RDF objects.
        if self.rdf_xlsx != "":
            self.rdf = self._rdf_maker(self.rdf_xlsx, charset=self.charset)
            self.rdf.make()

        # create METS from @self.mets_template.
        self.mets = self._mets_maker(self.mets_template, charset=self.charset,
                TIMESTAMP = lambda: datetime.utcnow().isoformat() + "Z", 
                EVENTS = self.preservation_events,
                FOLDERS = self.directory.dirs, 
                FILES = self.directory.files,
                GRAPH = "\n" + self.directory.rdirs.ls(),
                RDFS = self.rdf.rdfs if self.rdf is not None else [])
        self.mets.make()
        
        # if the METS template failed to render, return AIP and mark it invalid.
        if self.mets.xml is None:
            self.logger.warning("Couldn't create METS; invalidating AIP.")
            return (aip_dir, None, False)
        
        # set the METS file path.
        mets_file = "{}.mets.xml".format(self.account_id)
        mets_path = os.path.join(self.destination_dir, self.account_id, mets_file)
        mets_path = self._abspath(mets_path)
        
        # write @mets to file.
        with open(mets_path, "w", encoding=self.charset) as mf:
            mf.write(self.mets.xml)
            
        # determine if both the AIP and the METS are valid.
        validity = bool(self.aip.validate() * self.mets.validate())

        return (aip_dir, mets_file, validity)


# TEST.
if __name__ == "__main__":

    logging.basicConfig(level="DEBUG")

    p = Packager("foo", 
            "../tests/sample_files/hot_folder", 
            "../tests/sample_files", 
            "../mets_templates/test.xml",
            {"20180101":["fooevent", None]})
    
    aip = p.package()
    print(aip)
    pass
