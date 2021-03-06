#!/usr/bin/env python3

""" This module contains a class for constructing a TOMES Archival Information Package (AIP)
with a METS file and a METS manifest file. """

__NAME__ = "tomes_packager"
__FULLNAME__ = "TOMES Packager"
__DESCRIPTION__ = "Part of the TOMES project: creates a TOMES Archival Information Package."
__URL__ = "https://github.com/StateArchivesOfNorthCarolina/tomes-packager"
__VERSION__ = "0.0.1"
__AUTHOR__ = "Nitin Arora",
__AUTHOR_EMAIL__ = "nitin.a.arora@ncdcr.gov"

# import modules.
import sys; sys.path.append("..")
import hashlib
import logging
import logging.config
import os
import plac
import sys
import time
import yaml
from datetime import datetime
from tomes_packager.lib.aip_maker import AIPMaker
from tomes_packager.lib.directory_object import DirectoryObject
from tomes_packager.lib.premis_object import PREMISObject
from tomes_packager.lib.mets_maker import METSMaker
from tomes_packager.lib.rdf_maker import RDFMaker


class Packager():
    """ A class for constructing a TOMES Archival Information Package (AIP) with a METS file 
    and a METS manifest file. 
    
    Example:
        >>> from os.path import isfile
        >>> pkgr = Packager(account_id="foo", 
                source_dir="../tests/sample_files/hot_folder",
                destination_dir="../tests/sample_files")
        >>> pkgr.mets_path # "../tests/sample_files/foo/foo.mets.xml"
        >>> isfile(pkgr.mets_path) # False
        >>> pkgr.package() # True
        >>> pkgr.aip_dir #  "../tests/sample_files/foo"
        >>> isfile(pkgr.mets_path) # True
        >>> 
        >>> # to validate an existing AIP without moving files, pass in the parent directory
        >>> # as both the source and destination.
        >>> validation = Packager("foo", "../tests/sample_files", "../tests/sample_files")
        >>> validation.package() # True
        >>> 
        >>> # to create a new METS file in the existing AIP, override @mets_path.
        >>> repkg = Packager("foo", "../tests/sample_files", "../tests/sample_files",
                manifest_template="",
                premis_log="../tests/sample_files/sample_premis.log",
                rdf_xlsx="../tests/sample_files/sample_rdf.xlsx")
        >>> repkg.mets_path = "../tests/sample_files/foo/new_mets.xml"
        >>> repkg.package() # True
    """


    def __init__(self, account_id, source_dir, destination_dir, 
            mets_template="mets_templates/default.xml", 
            manifest_template="mets_templates/MANIFEST.XML", premis_log="", rdf_xlsx="", 
            charset="utf-8"):
        """ Sets instance attributes.

        Attributes:
            - aip_dir (str): The path to the AIP.
            - aip_obj (AIPMaker): The object version of the AIP located at @destination_dir.
            - directory_obj (DirectoryObject): The object version of @destination_dir.
            - premis_obj (PREMISObject): The preservation metadata created from @premis_log.
            - mets_obj (METSMaker): The METS object created from @mets_template.
            - manifest_obj (METSMaker): The METS object created from @manifest_template.
            - rdf_obj (RDFMaker): The RDF object created from @rdf_xlsx.
            - time_utc (function): Returns UTC time as ISO 8601.
            - time_local (function): Returns local time as ISO 8601 with UTC offset.
            - time_hash (function) Returns the last 7 characters of the SHA-256 version of
            time_utc().
           - string_hash (function) Returns an "h" followed by the last 7 characters of the 
           SHA-256 version of a required string argument.
            - mets_path (str): The file path for the METS file. If needed, this can be 
            manually overridden prior to running .package().
            - manifest_path (str): The file path for the METS manifest file. As with 
            @mets_path, this can be manually overridden.
            - packager_mod (module): The package.py module itself. This provides access to 
            global metadata. Example: ".packager_mod.__VERSION__".
        
        Args:
            - account_id (str): The email account's base identifier, i.e. the file prefix.
            - source_dir (str): The folder path from which to transfer data.
            - destination_dir (str): The folder path in which to create the AIP structure.
            - mets_template (str): The file path for the METS template. This will be used to
            render a METS file inside the AIP's root folder. Pass in an empty string to bypass
            file creation.
            - manifest_template (str): The file path for the METS manifest template. 
            This will be used to render a METS manifest file inside the AIP's root folder. 
            Pass in an empty string to bypass file creation.
            - premis_log (str): Optional preservation metadata data file to pass into 
            METS templates.
            - rdf_xlsx (str): Optional Excel 2010+ (.xlsx) RDF/Dublin Core file to pass into 
            METS templates.
            - charset (str): The encoding for the rendered METS file/s and the RDF XML in
            @rdf_obj.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience functions to clean up path notation.
        self._normalize_sep = lambda p: p.replace(os.sep, os.altsep) if (
                os.altsep == "/") else p
        self._normalize_path = lambda p: self._normalize_sep(os.path.normpath(p)) if (
                p != "") else ""
        self._join_paths = lambda *p: self._normalize_path(os.path.join(*p))

        # set @account_id; log a warning if it isn't a valid identifier.
        self.account_id = str(account_id)
        if not self.account_id.isidentifier():
            non_id_chars = [c for c in self.account_id if not c.isalnum() and c != "_"]
            msg = "@account_id contains non-identifier characters: {}; problems may arise."
            msg = msg.format(non_id_chars)
            self.logger.warning(msg)
        
        # set attributes.
        self.source_dir = self._normalize_path(source_dir)
        self.destination_dir = self._normalize_path(destination_dir)
        self.premis_log = self._normalize_path(premis_log)
        self.mets_template = self._normalize_path(mets_template)
        self.manifest_template = self._normalize_path(manifest_template)
        self.rdf_xlsx = self._normalize_path(rdf_xlsx)
        self.charset = charset

        # set module attribute.
        self.packager_mod = sys.modules[__name__]

        # set attributes for imported classes.
        self._aip_maker_cls = AIPMaker
        self._directory_object_cls = DirectoryObject
        self._premis_object_cls = PREMISObject
        self._mets_maker_cls = METSMaker
        self._rdf_maker_cls = RDFMaker

        # set attributes for constructed objects.
        self.aip_dir = self._join_paths(self.destination_dir, self.account_id)
        self.aip_obj = None
        self.directory_obj = None
        self.premis_obj = None
        self.mets_obj = None
        self.manifest_obj = None
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

        # set template-accessible functions.
        self.time_utc = lambda: datetime.utcnow().isoformat() + "Z"
        self.time_local = lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z")
        self.time_hash = lambda: hashlib.sha256(self.time_utc().encode(
            self.charset)).hexdigest()[:7]
        self.string_hash = lambda s: "h" + hashlib.sha256(s.encode(self.charset)).hexdigest(
                )[:7]


    def write_mets(self, filename, template, xsd_validation=False, **kwargs):
        """ Writes a METS file to the given @filename path using the given METS @template.

        Args:
            - filename (str): The relative file path for the outputted METS file. The file 
            will be placed inside the AIP directory.
            - template (str): The path to the METS Jinja template file.
            - xsd_validation (bool): Use True to validate the METS via the METS XSD. Use False
            to simply determine if the METS file was written or not (i.e. for files too large
            to validate).
            - **kwargs: Any optional keyword arguments to pass into the METS @template. Note
            that the key "SELF" is reserved as @self is automatically passed into the template
            as "SELF".
        
        Returns:
            tuple: The return value.
            The first item is a METSMaker object. None if the METS couldn't be created.
            The second item is a boolean. This is True if the METS file is valid and 
            @xsd_validation is True OR if @xsd_validation is False and the METS file is a real
            file. Otherwise, this is False.
        """

        self.logger.info("Writing METS file '{}' from template: {}".format(
            filename, template))

        # if "SELF" is in @kwargs, remove it.
        if "SELF" in kwargs:
            self.logger.warning("Removing reserved key 'SELF' from @kwargs.")
            kwargs.pop("SELF")

        # pass @self and @kwargs into @template and render it; determine validity.
        try:
            mets_obj = self._mets_maker_cls(template, filename, charset=self.charset, 
                    SELF=self, **kwargs)
            mets_obj.make()
            if xsd_validation:
                is_valid = mets_obj.validate()
            else:
                is_valid = os.path.isfile(mets_obj.filepath)
        except Exception as err:
            self.logger.warning("Can't complete METS file '{}' from template: {}".format(
                filename, template))
            self.logger.error(err)
            mets_obj = None
            is_valid = False

        return (mets_obj, is_valid)


    def package(self):
        """ Creates the AIP structure and METS file. Note: if @self.source_dir and
        @self.destination_dir are the same then no files will be moved, but the AIP will still
        be validated and METS files will be created.

        Returns:
            bool: The return value.
            True if the overall AIP structure appears to be valid AND any optional METS files
            appear to be valid. Otherwise, False.
        """

        self.logger.info("Packaging: {}".format(self.aip_dir))

        # create AIP structure.
        self.aip_obj = self._aip_maker_cls(self.account_id, self.source_dir, 
                self.destination_dir)
        self.aip_obj.make()
        is_aip_valid = self.aip_obj.validate()

        # if the AIP structure isn't valid, return False.
        if not is_aip_valid:
            self.logger.warning("AIP structure appears to be invalid; aborting.")
            return is_aip_valid

        # if no METS templates were passed; return AIP validity.
        if self.mets_template == "" and self.manifest_template == "":
            self.logger.info("No METS or manifest templates passed; skipping METS creation.")
            return is_aip_valid

        # create a DirectoryObject.
        self.directory_obj = self._directory_object_cls(self.aip_dir)

        # if needed, create a PREMISObject.
        if self.premis_log != "":
            events = self._premis_object_cls.load_file(self.premis_log)
            self.premis_obj = self._premis_object_cls(events)

        # if needed, create an RDFObject.
        if self.rdf_xlsx != "":
            self.rdf_obj = self._rdf_maker_cls(self.rdf_xlsx, charset=self.charset)
            self.rdf_obj.make()
            
        # if needed, write the METS file.
        if self.mets_template != "":
            self.logger.info("Creating main METS file for AIP.")
            self.mets_obj, is_mets_valid = self.write_mets(self.mets_path, self.mets_template,
                    True)
        else:
            self.logger.info("No METS template passed.")
            is_mets_valid = True

        # if needed, write the METS manifest.
        if self.manifest_template != "":
            self.logger.info("Creating METS manifest file for AIP.")            
            self.manifest_obj, is_manifest_valid = self.write_mets(self.manifest_path, 
                    self.manifest_template)
        else:
            self.logger.info("No manifest template passed.")            
            is_manifest_valid = True
        
        # determine overall AIP validity.
        is_valid = bool(is_aip_valid * is_mets_valid * is_manifest_valid)
        
        # report overall AIP validity.
        if is_valid:
            self.logger.info("Final AIP appears to be valid.")
        else:
            if not is_aip_valid:
                self.logger.warning("Couldn't create valid AIP structure.")
            if not is_mets_valid:
                self.logger.warning("Couldn't create valid METS: {}".format(self.mets_path))
            if not is_manifest_valid:
                self.logger.warning("Couldn't create valid METS manifest: {}".format(
                    self.manifest_path))
            self.logger.warning("Final AIP appears to be invalid.")
            self.logger.info("Manual intervention might be needed to fix the AIP.")
        
        return is_valid


# CLI.
def main(account_id: ("email account identifier"), 
        source_dir: ("path to email \"hot folder\""),
        destination_dir: ("AIP destination path"),
        silent: ("disable console logs", "flag", "s"),
        mets_template: ("path to METS template", "option")="mets_templates/default.xml",
        manifest_template: ("path to METS manifest template", "option")=\
                "mets_templates/MANIFEST.XML",
        premis_log: ("path to preservation metadata log", "option")="",
        rdf_xlsx: ("path to RDF/Dublin Core .xlsx file", "option")=""):

    "Creates a TOMES Archival Information Package.\
    \nexample: `python3 packager.py foo ../tests/sample_files/hot_folder ../tests/sample_files`\
    \n\nNote: If \"../tests/sample_files/foo\" already exists, run\
    \n`python3 ../tests/sample_files/reset_hot_folder.py` to reset the hot folder."

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
            manifest_template, premis_log, rdf_xlsx)
    
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
    plac.call(main)
