#!/usr/bin/env python3

""" This module contains a class for storing PREMIS compatible preservation metadata as an 
object. """

# import modules.
import dateutil.parser
import dateutil.tz
import logging
import logging.config


class PREMISObject(object):
    """ A class for storing PREMIS compatible preservation metadata as an object.
    
    Attributes:
        - agents (list): A list of agents data.
        - events (list): A list of event data.
        - objects (list): A list of objects data.

    Example:
        >>> data = [{"2018-05-17T12:40:52-0400": {"type": "agent", "alias":
        "pst2mime_converter", "name": "TOMES PST Converter", "version": "1"}},
        {"2018-05-17T12:40:53-0400": {"type": "event", "alias": "pst2mime",
        "description": "PST to MIME converted.", "agent": "pst2mime_converter"}}]
        >>> po = PREMISObject(data)
        >>> po.make()
        >>> po.events # ['pst2mime']
        >>> po.events[0].alias # 'pst2mime'
        >>> po.events[0].agent # 'pst2mime_converter'
        >>> po.events[0].timestamp # '2018-05-16T23:29:18.245000Z'
        >>> po[0].agent # '[pst2mime_converter]'
        >>> po.agents[0] == po.events[0].agent # True
        >>> po.agents[0].__dict__ # show key/value pairs.
    """

    def __init__(self, premis_list):
        """ Sets instance atttributes.

        Args:
            - premis_list (list): Each item is a dict with an ISO timestamp as key
            and a dict as its value with required attributes "alias" (str) and "type" with
            one of the following values: "agent", "event", or "object".
            Additional attributes may also exist.

        Raises:
            - TypeError: If @premis_list is not a list.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # verify @premis_list is a dict.
        if not isinstance(premis_list, list):
            msg = "Expected list, got: {}".format(type(premis_list))
            self.logger.error(msg)
            raise TypeError(msg)
        
        # set attributes.
        self.premis_list = premis_list
        self.agents = []
        self.events = []
        self.objects = []
        self._type_map = {"agent": self.agents, "event": self.events, "object": self.objects}

            
    def _get_timestamp(self, timestamp):
        """ Converts a validate date string to ISO 8601 time. 
        
        Args:
            - timestamp (str): A date string, ideally already ISO 8601.

        Raises:
            - ValueError: If @timestamp cannot be parsed as a date.
        """
        
        # convert @timestamp to ISO format.
        try:
            timestamp = dateutil.parser.parse(timestamp).isoformat()
        except (TypeError, ValueError) as err:
            msg = "Invalid timestamp: {}".format(timestamp)
            self.logger.error(msg)
            raise ValueError(msg)
        
        return timestamp


    def _validate_metadata(self, metadata):
        """ ???

        Args:
            - metadata (dict): ???
        
        Returns:
            dict: Th return value.

        Raises:
            - TypeError: If the value of an item in @self.premis_list isn't itself a dict.
            - KeyError: If the value of an item in @self.premis_list doesn't contain the 
            keys "alias" and "type".
            - ValueError: If the "type" key's value doesn't equal "agent", "event", or 
            "object".
        """

        # make sure @metadata is a dict.
        if not isinstance(metadata, dict):
            msg = "Expected metadata to be a dict; got: {}".format(type(metadata))
            self.logger.error(msg)
            raise TypeError(msg)

        # make sure the key "alias" exists.
        if "alias" not in metadata:
            msg = "Missing required key: alias"
            self.logger.error(msg)
            raise KeyError(msg)

        # make sure the key "type" exists.
        if "type" not in metadata:
            msg = "Missing required key: type"
            self.logger.error(msg)
            raise KeyError(msg)

        # make sure key "type" has a legal value.
        legal_types = [t for t in self._type_map.keys()]
        if metadata["type"] not in legal_types:
            msg = "Key 'type' has illegal value '{}'; must be one of: {}".format(
                    metadata["type"], legal_types)
            self.logger.error(msg)
            raise ValueError(msg)

        # if "timestamp" is a key, delete it.
        if "timestamp" in metadata:
            msg = "Removing key 'timestamp' as it will be computed."
            self.logger.warning(msg)
            metadata.pop("timestamp")

        return metadata


    def make(self):
        """ Processes events in @premis_list ???

        Raises:
            - TypeError: ???
            - ValueError: ???
        """
            
        self.logger.info("Parsing data.")
        
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
            key = [k for k in data][0]
            timestamp = self._get_timestamp(key)
            metadata = data[key]
            
            self.logger.info("Processing: {}: {}".format(timestamp, metadata))
            
            # validate @data.
            metadata = self._validate_metadata(metadata)
            
            # create _MetadataObject.
            class _MetadaObject(str):
                pass
            md_obj = _MetadaObject(metadata["alias"])

            # set @md_obj attributes.
            for key in metadata:
                val = str(metadata[key])
                setattr(md_obj, key, val)
            md_obj.timestamp = timestamp      
            
            # append @md_obj to the correct attribute in @self.
            self_attr = self._type_map[md_obj.type]
            if md_obj.timestamp in self_attr:
                self.logger.warning("Data '{}' already in '{}'; resetting value.".format(
                    md_obj.timestamp, self_attr))
            self_attr.append(md_obj)

        return


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    data = [{"2018-05-17T12:40:52-0400": {"type": "agent", "alias":
        "pst2mime_converter", "name": "TOMES PST Converter", "version": "1"}},
        {"2018-05-17T12:40:53-0400": {"type": "event", "alias": "pst2mime",
        "description": "PST to MIME converted.", "agent": "pst2mime_converter"}}]
    po = PREMISObject(data)
    po.make()
    logging.info(po.events[0].timestamp)
    pass
