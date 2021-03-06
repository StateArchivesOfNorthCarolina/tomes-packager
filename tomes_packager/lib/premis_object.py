#!/usr/bin/env python3

""" This module contains a class for storing PREMIS compatible preservation metadata as an 
object. """

# import modules.
import dateutil.parser
import dateutil.tz
import logging
import logging.config
import os
import yaml


class PREMISObject(object):
    """ A class for storing PREMIS compatible preservation metadata as an object.
    
    Attributes:
        - agents (list): A list of PREMIS Agent data.
        - events (list): A list of PREMIS Event data.
        - objects (list): A list of PREMIS Object data.

    Example:
        >>> data = [{"2018-05-17T12:40:52-0400": {"entity": "agent", "name":
        "pst2mime_converter", "name": "TOMES PST Converter", "version": "1"}},
        {"2018-05-17T12:40:53-0400": {"entity": "event", "name": "pst2mime",
        "description": "PST to MIME converted.", "agent": "pst2mime_converter"}}]
        >>> po = PREMISObject(data)
        >>> po.events # ["pst2mime"]
        >>> po.events[0].name # "pst2mime"
        >>> po.events[0].agent # "pst2mime_converter"
        >>> po.events[0].timestamp # "2018-05-17T12:40:53-04:00"
        >>> po.agents[0] # ["pst2mime_converter"]
        >>> po.agents[0].__dict__ # show key/value pairs.
        >>> 
        >>> # to load data from a file ...
        >>> data = PREMISObject.load_file("../../tests/sample_files/sample_premis.log")
        >>> po2 = PREMISObject(data)
    """


    def __init__(self, premis_list):
        """ Sets instance atttributes.

        Args:
            - premis_list (list): Each item is a dict with an ISO timestamp as key and a dict
            as its value with required attributes "name" (str) and "entity" (str). The value
            for "name" can be any token, although whitespace is not technically banned. The
            only value options for "entity" are: "agent", "event", or "object". Additional 
            attributes may also exist. Note that the attribute "timestamp" is reserved as it
            is created automatically. Its value will be equal to the key itself, i.e. the ISO
            timestamp. 

        Raises:
            - TypeError: If @premis_list is not a list.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # verify @premis_list is a list.
        if not isinstance(premis_list, list):
            msg = "Expected list, got: {}".format(type(premis_list))
            self.logger.error(msg)
            raise TypeError(msg)
        
        # set attributes.
        self.premis_list = premis_list
        self.agents = []
        self.events = []
        self.objects = []
        self._entity_map = {"agent": self.agents, "event": self.events, 
                "object": self.objects}
        self._required_keys = ["name", "entity"]
    
        # populate attributes.
        self._get_data()

            
    def _get_timestamp(self, timestamp):
        """ Converts a validate date string to ISO 8601. 
        
        Args:
            - timestamp (str): A date string, ideally already ISO 8601.

        Raises:
            - ValueError: If @timestamp cannot be parsed as a date.
        """
       
        self.logger.debug("Formatting timestamp: {}".format(timestamp))

        # convert @timestamp to ISO format.
        try:
            timestamp = dateutil.parser.parse(timestamp).isoformat()
        except (TypeError, ValueError) as err:
            msg = "Invalid timestamp: {}".format(timestamp)
            self.logger.warning(msg)
            self.logger.error(err)
            raise ValueError(msg)
        
        return timestamp


    def _sanitize_metadata(self, metadata):
        """ Verifies @metadata is a dict with the required keys in @self._required_keys.
        Also verifies the key "entity" has a value in @self._entity_map.

        Args:
            - metadata (dict): The dictionary to validate.
        
        Returns:
            dict: The return value.
            This equals @metadata after it has been validated and stripped of bad keys. 

        Raises:
            - TypeError: If @metadata isn't a dict.
            - KeyError: If @metadata doesn't contain the required keys in 
            @self._required_keys.
            - ValueError: If the "entity" key's value isn't in @self._entity_map.
        """

        self.logger.info("Sanitizing metadata.")

        # make sure @metadata is a dict.
        if not isinstance(metadata, dict):
            msg = "Expected metadata to be a dict; got: {}".format(type(metadata))
            self.logger.error(msg)
            raise TypeError(msg)

        # check for required keys.
        for key in self._required_keys:
            if key not in metadata:
                msg = "Missing required key: {}".format(key)
                self.logger.error(msg)
                raise KeyError(msg)

        # make sure the "entity" key has a legal value.
        if metadata["entity"] not in self._entity_map:
            msg = "Key 'entity' has illegal value: {}; must be one of: {}".format(
                    metadata["entity"], list(self._entity_map))
            self.logger.error(msg)
            raise ValueError(msg)

        # if "timestamp" is a key, delete it.
        if "timestamp" in metadata:
            msg = "Removing key 'timestamp' as it will be computed."
            self.logger.warning(msg)
            metadata.pop("timestamp")

        return metadata


    def _get_data(self):
        """ Processes data items in @self.premis_list and stores the item in the appropriate 
        attribute list: @self.agents, @self.events, or @self.objects.

        Raises:
            - TypeError: If an item is not a dict.
            - ValueError: If an item doesn't have a length of 1.
        """
            
        self.logger.info("Parsing events.")
        
        for data in self.premis_list:

            # make sure @data is a dict.
            if not isinstance(data, dict):
                msg = "Expected data to be a dict; got: {}".format(type(data))
                self.logger.error(msg)
                raise TypeError(msg)

            # make sure @data only has one item.
            if len(data) != 1:
                msg = "Expected 1 data item, got: {}".format(len(data))
                self.logger.error(msg)
                raise ValueError(msg)
                
            # assign @data to variables.
            key = list(data)[0]
            timestamp = self._get_timestamp(key)
            metadata = data[key]
            
            self.logger.info("Processing event: {}: {}".format(timestamp, metadata))
            
            # validate @data.
            metadata = self._sanitize_metadata(metadata)
            
            # create metadata as object.
            class _MetadaObject(str):
                pass
            md_obj = _MetadaObject(metadata["name"])

            # set @md_obj attributes.
            for key in metadata:
                val = str(metadata[key])
                setattr(md_obj, key, val)
            md_obj.timestamp = timestamp      
            
            # append @md_obj to the correct attribute in @self.
            self_attr = self._entity_map[md_obj.entity]
            if md_obj in self_attr:
                self.logger.warning("Overwriting existing data in attribute: .{}s".format(
                    md_obj.entity))
                self_attr.remove(md_obj)
            else:
                self.logger.debug("Updating attribute: .{}s".format(md_obj.entity))
            self_attr.append(md_obj)

        return


    @staticmethod
    def load_file(premis_log, charset="utf-8"):
        """ Converts a @premis_log to a list.

        Args:
            - premis_log (str): The path to the PREMIS log file. Each line must be a YAML
            compatible dict that conforms to the rules for a @premis_list in 
            PREMISObject.__init__().
            - charset (str): The encoding with which to open @premis_log.

        Returns:
            list: The return value.
            None is returned if @premis_log can't be read into memory or isn't YAML 
            compatible.

        Raises:
            - FileNotFoundError: If @premis_log is not an actual file.
        """

        # add logger.
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.NullHandler())

        logger.info("Loading data in: {}".format(premis_log))

        # verify @premis_log is a file.
        if not os.path.isfile(premis_log):
            msg = ("Can't find: {}".format(premis_log))
            logger.error(msg)
            raise FileNotFoundError(msg)

        # open @premis_log and store each line in a list.
        try:
            data = open(premis_log, encoding=charset).readlines()
        except Exception as err:
            logger.warning("Can't read '{}' into memory; skipping.".format(premis_log))
            logger.error(err)
            return

        # convert each item in @data to YAML.
        i = 0
        for datum in data:
            try:
                data[i] = yaml.load(datum)
                i += 1
            except (yaml.parser.ParserError, yaml.scanner.ScannerError) as err:
                logger.warning("Can't parse line {} as YAML; aborting.".format(i + 1))
                logger.error(err)
                return

        return data


if __name__ == "__main__":
    pass
