""" This module contains a class for constructing a TOMES archival information package (AIP)
with an optional METS file and an optional METS manifest file.

Todo:
    * EVERY public method in all modules needs to start with a logging statement.
        - Probably privates too.
    * Make sure you can never return anything not yet defined (reference error).
    * Write unit tests.
    * Add CLI.
    * Run autoflakes on this and lib/* and unit tests.
    * Review this and module docstrings.
        - Examples that reference files should use real sample files.
    * Work on PREMIS logging for DarcMail, PST Converter, and Tagger.
    * Documentation and README.
"""

# import modules.
import hashlib
import logging
import logging.config
import os
import plac
import sys
import time
import yaml
from datetime import datetime
from lxml import etree
from lib.aip_maker import AIPMaker
from lib.directory_object import DirectoryObject
from lib.premis_object import PREMISObject
from lib.mets_maker import METSMaker
from lib.rdf_maker import RDFMaker

    
class Packager():
    """ A class for constructing a TOMES archival information package (AIP) with an optional 
    METS file and an optional METS manifest file. 
    
    Example:
        >>> from os.path import isfile
        >>> pkgr = Packager("foo", 
            "../tests/sample_files/hot_folder", 
            "../tests/sample_files/", 
            "../mets_templates/basic.xml",
            "../mets_templates/MANIFEST.XML",
            events_log="../tests/sample_files/sample_events.log",
            rdf_xlsx="../tests/sample_files/sample_rdf.xlsx",
            )
        >>> pkgr.mets_path # "../tests/sample_files/foo/foo.mets.xml"
        >>> isfile(pkgr.mets_path) # False
        >>> pkgr.package() # True
        >>> pkgr.aip_dir #  "../tests/sample_files/foo"
        >>> isfile(pkgr.mets_path) # True
        >>> pkg = Packager("foo", "../tests/sample_files", "../tests/sample_files")
        >>> pkg.package() # validates the existing AIP structure but doesn't move files.
    """


    def __init__(self, account_id, source_dir, destination_dir, mets_template="", 
            manifest_template="", events_log="", rdf_xlsx="", charset="utf-8"):
        """ Sets instance attributes.

        Attributes:
            - aip_dir (str): The path to the AIP.
            - aip_obj (AIPMaker): The object versio of the AIP located at @destination_dir.
            - directory_obj (DirectoryObject): The object version of @destination_dir.
            - premis_obj (PREMISObject): The preservation metadata provided in @events_log.
            - mets_obj (METSMaker): The METS object created from @mets_template.
            - rdf_obj (RDFMaker): The RDF object created from @rdf_xlsx.
            - time_utc (function): Returns UTC time as ISO 8601.
            - time_local (function): Returns local time as ISO 8601 with UTC offset.
            - time_hash (function) Returns the last 7 characters of the SHA-256 version of
            time_utc().
            - mets_path (str): The file path for the METS file. If needed, this can be 
            manually overridden prior to running .package().
            - manifest_path (str): The file path for the METS manifest file. As with 
            @mets_path, this can be manually overridden.
        
        Args:
            - account_id (str): The email account's base identifier, i.e. the file prefix.
            - source_dir (str): The folder path from which to transfer data.
            - destination_dir (str): The folder path in which to create the AIP structure.
            - mets_template (str): The file path for the METS template. This will be used to
            render a METS file inside the AIP's root folder.
            - manifest_template (str): The file path for the METS manifest template. 
            This will be used to render a METS manifest file inside the AIP's root folder.
            - events_log (str): Optional preservation metadata file to pass into 
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
        self._join_paths = lambda *p: self._normalize_path(os.path.join(*p))        

        # set attributes.
        self.account_id = str(account_id) 
        self.source_dir = self._normalize_path(source_dir)
        self.destination_dir = self._normalize_path(destination_dir)
        self.events_log = events_log
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
        self.aip_dir = self._join_paths(self.destination_dir, self.account_id)
        self.aip_obj = None
        self.directory_obj = None
        self.premis_obj = None
        self.mets_obj = None
        self._manifest_obj = None
        self.rdf_obj = None           

        # set METS paths.
        self.mets_path = None
        if self.mets_template != "":
            mets_path = "{}.mets.xml".format(self.account_id)
            self.mets_path = self._join_paths(self.destination_dir, self.account_id, 
                    mets_path)

        self.manifest_path = None        
        if self.manifest_template != "":
            manifest_path = "{}.mets.manifest".format(self.account_id)
            self.manifest_path = self._join_paths(self.destination_dir, self.account_id,
                    manifest_path)

        # set template-accessible time functions.
        self.time_utc = lambda: datetime.utcnow().isoformat() + "Z"
        self.time_local = lambda: time.strftime("'%Y-%m-%dT%H:%M:%S%z'")[1:-1]
        self.time_hash = lambda: hashlib.sha256(self.time_utc().encode(
            self.charset)).hexdigest()[:7]


    def write_mets(self, filename, template, xsd_validation=True, **kwargs):
        """ Writes a METS file to the given @path using the given METS @template.

        Args:
            - filename (str): The relative file path for the outputted METS file. The file 
            will be placed inside the AIP directory.
            - template (str): The path to the METS Jinja template file.
            - xsd_validation (bool): Use True to validate the METS via the METS XSD. Use False
            to simply determine if the METS file was written or not.
            - **kwargs: Any optional keyword arguments to pass into the METS @template.
        
        Returns:
            tuple: The return value.
            The first item is a METSMaker object. None if the METS couldn't be created.
            The second item is a boolean. This is True if the METS file is valid and 
            @xsd_validation is True OR if @xsd_validation is False and the METS file is a real
            file. Otherwise, this is False.
        """

        # create a DirectoryObject.
        if self.directory_obj is None:
            self.directory_obj = self._directory_object(self.aip_dir)

        # if needed, create a PREMISObject.
        if self.events_log != "" and self.premis_obj is None:
            events = self._premis_object.load_file(self.events_log)
            self.premis_obj = self._premis_object(events)

        # if needed, create an RDFObject.
        if self.rdf_xlsx != "" and self.rdf_obj is None:
            self.rdf_obj = self._rdf_maker(self.rdf_xlsx, charset=self.charset)
            self.rdf_obj.make()

        # add @self to @kwargs so that it can be called in METS templates.
        kwargs["SELF"] = self

        # create the METS file from @template; determine validity.
        try:
            mets_obj = self._mets_maker(template, filename, charset=self.charset, **kwargs)
            mets_obj.make()
            if xsd_validation:
                is_valid = mets_obj.validate()
            else:
                is_valid = os.path.isfile(mets_obj.filepath)
        except Exception as err:
            self.logger.warning("Can't write METS file '{}' from template: {}".format(
                filename, template))
            mets_obj = None
            is_valid = False

        return (mets_obj, is_valid)


    def package(self):
        """ Creates the AIP structure and optional METS file. Note: if @self.source_dir and
        @self.destination_dir are the same, then no files will be moved, however the AIP
        will still be validated and optional METS files created.

        Returns:
            bool: The return value.
            True if the overall AIP structure and any METS files appear to be valid. 
            Otherwise, False.
        """

        # set AIP path.
        self.logger.info("Packaging: {}".format(self.aip_dir))

        # create AIP structure.
        self.aip_obj = self._aip_maker(self.account_id, self.source_dir, self.destination_dir)
        if self.source_dir != self.destination_dir:
            self.aip_obj.make()
        else:
            self.logger.info("Source path equals destination path; no files will be moved.")
        is_aip_valid = self.aip_obj.validate()

        # if the AIP structure isn't valid, warn but continue on.
        if not is_aip_valid:
            self.logger.warning("AIP structure is invalid; continuing anyway.")

        # if no METS templates were passed; return AIP validity.
        if self.mets_template == "" and self.manifest_template == "":
            self.logger.info("No METS templates passed; skipping METS creation.")
            return is_aip_valid

        # if needed, set the METS file path and make the METS file.
        if self.mets_template != "":
            self.logger.info("Creating main METS file for AIP.")
            self.mets_obj, is_mets_valid = self.write_mets(self.mets_path, self.mets_template)
        else:
            is_mets_valid = True

        # if needed, write the METS manifest.
        if self.manifest_template != "":
            self.logger.info("Creating METS manifest file for AIP.")            
            self._manifest_obj, is_manifest_valid = self.write_mets(self.manifest_path, 
                    self.manifest_template, False)
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


# CLI.
def main(account_id: "email account identifier", 
        source_dir: ("path to email accounts hot-folder"),
        destination_dir: ("AIP destination path"),
        silent: ("disable console logs", "flag", "s"),
        mets_template: ("METS template")="",
        manifest_template: ("METS manifest template")="../mets_templates/MANIFEST.XML",
        events_log: ("preservation metadata log file")="",
        rdf_xlsx: (".xlsx RDF/Dublin Core file")=""):

    "Creates a TOMES Archival Information Package.\
    \nexample: `py -3 packager.py foo ../tests/sample_files/hot_folder ../tests/sample_files`"

    # make sure logging directory exists.
    logdir = "log"
    if not os.path.isdir(logdir):
        os.mkdir(logdir)

    # get absolute path to logging config file.
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(config_dir, "logger.yaml")
    
    # load logging config file.
    with open(config_file) as cf:
        config = yaml.safe_load(cf.read())
    if silent:
        config["handlers"]["console"]["level"] = 100
    logging.config.dictConfig(config)
    
    # create class instance.
    packager = Packager(account_id, source_dir, destination_dir, mets_template, 
            manifest_template, events_log, rdf_xlsx)
    
    # package the email account.
    logging.info("Running CLI: " + " ".join(sys.argv))
    try:
        packager.package()
        logging.info("Done.")
        sys.exit()
    except Exception as err:
        logging.critical(err)
        sys.exit(err.__repr__())
        

if __name__ == "__main__":
    
    import plac
    #plac.call(main)

    logging.basicConfig(level="DEBUG")

    pkgr = Packager("foo", 
            "../tests/sample_files/hot_folder", 
            "../tests/sample_files/", 
            "../mets_templates/basic.xml",
            "../mets_templates/MANIFEST.XML",
            events_log="../tests/sample_files/sample_events.log",
            #rdf_xlsx="../tests/sample_files/sample_rdf.xlsx",
            )

    aip = pkgr.package()
    print(aip)
    print(pkgr.mets_path)
    print(os.path.isfile(pkgr.mets_path))
