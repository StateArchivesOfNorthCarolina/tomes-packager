""" This module contains a class for constructing a TOMES archival information package (AIP)
with an optional METS file and an optional METS manifest file.

Todo:
    * EVERY public method in all modules needs to start with a logging statement.
        - Probably privates too.
    * If AIP restructing works but METS fails, we need a function to JUST
    drop in the METS (and to create DirectoryObject) - also useful if AIP 
    already exists.
        - Use self.write_mets().
    * Run autoflakes on this and lib/*.
    * Gotta work on PREMISObject stuff here.
    * Add CLI.
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
from lib.premis_object import PREMISObject
from lib.mets_maker import METSMaker
from lib.rdf_maker import RDFMaker

    
class Packager():
    """ A class for constructing a TOMES archival information package (AIP) with an optional 
    METS file and an optional METS manifest file. """


    def __init__(self, account_id, source_dir, destination_dir, mets_template="", 
            manifest_template="", preservation_data=[], rdf_xlsx="", charset="utf-8"):
        """ Sets instance attributes.

        Attributes:
            - aip_obj = ???
            - directory_obj = ???
            - premis_obj = ???
            - mets_obj = ???
            - rdf_obj = ???
            - mets_path = ???
            - manifest_path = ???
        
        Args:
            - account_id (str): The email account's base identifier, i.e. the file prefix.
            - source_dir (str): The folder path from which to transfer data.
            - destination_dir (str): The folder path in which to create the AIP structure.
            - mets_template (str): The file path for the METS template. This will be used to
            render a METS file inside the AIP's root folder.
            - manifest_template (str): The file path for the METS manifest template. 
            This will be used to render a METS manifest file inside the AIP's root folder.
            - preservation_data (PreservationObject): Optional preservation data to pass into
            @mets_template.
            - rdf_xlsx (str): The Excel 2010+ (.xlsx) file from which to create RDFs. 
            - charset (str): The encoding for the rendered METS an RDF data.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # suppress verbose DirectoryObject and FileObject logging.
        logging.getLogger("lib.directory_object").setLevel(logging.INFO)
        logging.getLogger("lib.file_object").setLevel(logging.WARNING)

        # convenience functions to clean up path notation.
        self._normalize_path = lambda p: os.path.normpath(p).replace("\\", "/")
        self._abspath = lambda p: self._normalize_path(os.path.abspath(p))
        self._join_paths = lambda *p: self._normalize_path(os.path.join(*p))        

        # set attributes.
        self.account_id = str(account_id) 
        self.source_dir = self._normalize_path(source_dir)
        self.destination_dir = self._normalize_path(destination_dir)
        self.preservation_data = preservation_data
        self.mets_template = mets_template
        self.manifest_template = manifest_template
        self.rdf_xlsx = rdf_xlsx
        self.charset = charset

        # set attributes for imported classes.
        self._aip_maker = AIPMaker
        self._directory_object = DirectoryObject
        self._premis_object = PREMISObject
        self._mets_maker = METSMaker
        self._rdf_maker = RDFMaker

        # creates atttibutes for constructed objects.
        self.aip_obj = None
        self.directory_obj = None
        self.premis_obj = None
        self.mets_obj = None
        self._manifest_obj = None
        self.rdf_obj = None
        self.mets_path = "{}.mets.xml".format(self.account_id)
        self.manifest_path = "{}.mets.manifest".format(self.account_id)


    def write_mets(self, filename, template, xsd_validation=True, *args, **kwargs):
        """ Writes a METS file to the given @path using the given METS @template.

        Args:
            - filename (str): The relative file path for the outputted METS file. The file 
            will be placed inside the AIP directory.
            - template (str): The path to the METS template file.
            - xsd_validation (bool): Use True to validate the METS via the METS XSD. Use False
            to simply determine if the METS file was written or not.
        
        Returns:
            tuple: The return value.
            The first item is a METSMaker object.
            The second item is a boolean. This is True if the METS file is valid and 
            @xsd_validation is True OR if @xsd_validation is False and the METS file is a real
            file. Otherwise, this is False.
        """

        # set path for writing METS file.
        mets_path = os.path.join(self.destination_dir, self.account_id, filename)
        mets_path = self._abspath(mets_path)

        # create the METS file from @template; determine validity.
        try:
            mets_obj = self._mets_maker(template, mets_path, charset=self.charset, **kwargs)
            mets_obj.make()
            if xsd_validation:
                is_valid = mets_obj.validate()
            else:
                is_valid = os.path.isfile(mets_obj.filepath)
        except Exception as err:
            self.logger.warning("Can't write METS file '{}' from template: {}".format(
                mets_path, template))
            is_valid = False

        return (mets_obj, is_valid)


    def package(self):
        """ Creates the AIP structure and optional METS file.
        
        Returns:
            bool: The return value.
            True if the overall AIP structure and any METS files appear to be valid. 
            Otherwise, False.
        """

        # set AIP path.
        aip_dir = self._abspath(os.path.join(self.destination_dir, self.account_id))
        self.logger.info("Packaging: {}".format(aip_dir))

        # create AIP structure.
        self.aip_obj = self._aip_maker(self.account_id, self.source_dir, self.destination_dir)
        self.aip_obj.make()
        is_aip_valid = self.aip_obj.validate()

        # if the AIP structure isn't valid, warn but continue on.
        if not is_aip_valid:
            self.logger.warning("AIP structure is invalid; continuing anyway.")

        # if no METS templates were passed; return AIP data.
        if self.mets_template == "" and self.manifest_template == "":
            self.logger.info("No METS templates passed; skipping METS creation.")
            return (aip_dir, None, self.aip_obj.validate())

        # create a DirectoryObject for the AIP.
        self.directory_obj = self._directory_object(aip_dir)

        # create a PREMISObject.
        self.premis_obj = self._premis_object(self.preservation_data)

        # if needed, create RDF objects.
        if self.rdf_xlsx != "":
            self.rdf_obj = self._rdf_maker(self.rdf_xlsx, charset=self.charset)
            self.rdf_obj.make()

        # set keyword arguments to send to METS templates.
        kwargs = {"SELF": self,
                "TIMESTAMP": lambda: datetime.utcnow().isoformat() + "Z",
                "ACCOUNT": self.account_id,
                "AGENTS": self.premis_obj.agents,
                "EVENTS": self.premis_obj.events,
                "OBJECTS": self.premis_obj.objects,
                "FOLDERS": self.directory_obj.dirs, 
                "FILES": self.directory_obj.files,
                "RDFS": self.rdf_obj.rdfs if self.rdf_obj is not None else []}
        
        # if needed, set the METS file path and make the METS file.
        if self.mets_template != "":
            self.logger.info("Creating main METS file for AIP.")
            self.mets_obj, is_mets_valid = self.write_mets(self.mets_path, self.mets_template,
                    **kwargs)
        else:
            is_mets_valid = True

        # if needed, write the METS manifest.
        if self.manifest_template != "":
            self.logger.info("Creating METS manifest file for AIP.")            
            self._manifest_obj, is_manifest_valid = self.write_mets(self.manifest_path, 
                    self.manifest_template, False, **kwargs)
        else:
            is_manifest_valid = True
        
        # determine overall AIP validity.
        is_valid = bool(is_aip_valid * is_mets_valid * is_manifest_valid)
        
        # report according to overall AIP validity.
        if is_valid:
            self.logger.info("Final AIP appears to be valid.")
        else:
            self.logger.warning("Final AIP appears to be invalid.")
            self.logger.info("Please manually investigate and fix the AIP.")
            if not is_aip_valid:
                self.logger.warning("Couldn't create valid AIP structure.")
                self.logger.info("Check the source files before fixing the AIP.")
            if not is_mets_valid:
                self.logger.warning("Couldn't create valid METS: {}".format(self.mets_path))
                self.logger.info("Check the METS template before fixing the AIP.")
            if not is_manifest_valid:
                self.logger.warning("Couldn't create valid METS manifest: {}".format(
                    self.manifest_path))
                self.logger.info("Check the METS manifest template before fixing the AIP.")

        return is_valid


if __name__ == "__main__":

    logging.basicConfig(level="DEBUG")

    p = Packager("foo", 
            "../tests/sample_files/hot_folder", 
            "../tests/sample_files", 
            "../mets_templates/basic_mets.xml",
            "../mets_templates/_MANIFEST.XML",
            rdf_xlsx="../tests/sample_files/sample_rdf.xlsx")
    
    aip = p.package()
    print(aip)
    pass
