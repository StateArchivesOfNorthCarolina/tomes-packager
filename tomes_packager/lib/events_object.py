#!/usr/bin/env python3

""" This module contains a class for storing one to many preservation events' data as an 
object. """

# import modules.
import dateutil.parser
import logging
import logging.config


class EventsObject(object):
    """ A class for storing one to many preservation events' data as an object.
    
    Attributes:
        - events (list): A list of event names. Each item is itself an attribute of the class
        instance with three sub-attributes: name (str), value (str), and timestamp (str). 

    Example:
        >>> d = {"2018-05-08T12:07:34-0400": ["pst_converted", None],
            "2018-05-08T12:07:24-0400": ["pst_converter", "readpst"]}
        >>> eo = EventsObject(d)
        >>> eo.events # ['pst_converted', 'pst_converter']
        >>> eo.pst_converted.name # 'pst_converted'
        >>> eo.pst_converted.value # None
        >>> eo.pst_converted.timestamp # '2018-05-08T12:07:34-04:00'
    """


    def __init__(self, events_dict):
        """ Sets instance atttributes.

        Args:
            - events_dict (dict): Each key is a timestamp; each value is a list. The first 
            item in the list is a string, the event's alias. The second item is additional
            information such as a filename that the event created or a boolean (to explicitly
            state that something occurred). If not needed, the second item can be None or 
            an empty string.

        Raises:
            - TypeError: If @events_dict is not a dict.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # verify @events_dict is a dict.
        if not isinstance(events_dict, dict):
            msg = "Expected dictionary, got: {}".format(type(events_dict))
            self.logger.error(msg)
            raise TypeError(msg)
        
        # set attributes.
        self.events_dict = events_dict
        self.events = []
        self.event_object = self._EventObject

        # process events in @events_dict.
        self._add_events()

            
    def _add_events(self):
        """ Processes events in @events_dict by adding each event's alias to @self.events
        and adding an attribute to @self.

        Raises:
            - TypeError: If the second item in one of @self.dict's values isn't a list.
            - ValueError: If the second item in one of @self.dict's values is not a list of 
            exactly two items.
        """
            
        self.logger.info("Parsing event dictionary.")
        
        for event in self.events_dict:

            self.logger.info("Storing event: {}".format(event))

            # assign data.
            timestamp = event
            event_list = self.events_dict[event]
            
            # make sure @event_list is a list of 2 items.
            if not isinstance(event_list, list):
                msg = "Expected item to be a list; got: {}".format(type(event_list))
                self.logger.error(msg)
                raise TypeError(msg)
            if len(event_list) != 2:
                msg = "Item value list must have exactly 2 items, got {}".format(
                        len(event_list))
                raise ValueError(msg)
            
            # create _EventObject.
            name, value = event_list
            value = self.event_object(name, value, timestamp)
            
            # append @name to @self.events.
            self.events.append(name)

            # add event as attribute of @self.
            if hasattr(self, name):
                self.logger.warning("Event '{}' already exists; resetting value.".format(
                    name))
            setattr(self, name, value)

        return


    class _EventObject(object):
        """ A class for storing a single preservation event's data as an object.

        Attributes:
            - name (str): The name of the event, i.e. its alias.
            - value (str): The event's value. Note: this will be None if no data was received.
            - timestamp (str): The event's timestamp (ISO 8601).
        """


        def __init__(self, name, value, timestamp):
            """ Sets instance attributes.
            
            Raises:
                - TypeError: If @name is not a string.
            """

            # verify @name is a string.
            if not isinstance(name, str):
                msg = "Expected string; got: {}".format(type(name))
                self.logger.error(msg)
                raise TypeError(msg)

            # set attributes.
            self.name = name
            self.value = str(value) if value not in ("", None) else None
            self.timestamp = self._convert_time(timestamp)

        
        def _convert_time(self, tstamp):
            """ Converts a validate date string to ISO 8601 time. 
            
            Args:
                - tstamp (str): A valid date string.

            Raises:
                - ValueError: If @tstamp cannot be parsed as a date.
            """

            try:
                timestamp = dateutil.parser.parse(tstamp).isoformat()
            except (TypeError, ValueError) as err:
                msg = "Invalid timestamp: {}".format(tstamp)
                self.logger.error(msg)
                raise ValueError(msg)
            
            return timestamp


if __name__ == "__main__":
    pass
