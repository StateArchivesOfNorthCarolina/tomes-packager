#!/usr/bin/env python3

""" This module contains a class for storing preservation event metadata as an object. """

# import modules.
import sys; sys.path.append("..")
import dateutil.parser
import logging
import logging.config


class EventsObject(object):
    """ A class for storing preservation event metadata as an object.
    
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


    def __init__(self, event_dict):
        """

        Args:
            - event_dict (dict):

        
        """

        # ???
        if not isinstance(event_dict, dict):
            #TODO:log
            raise TypeError
        
        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # ???
        self.event_dict = event_dict
        self.events = []
        self.event_object = self._EventObject

        # ???
        self._add_events()

            
    def _add_events(self):
        
        for event in self.event_dict:
            timestamp = event
            event_list = self.event_dict[event]
            if not isinstance(event_list, list):
                msg = "Logged event must be list; got: {}".format(type(event_list))
                self.logger.error(msg)
                raise TypeError(msg)
            if len(event_list) != 2:
                msg = "Logged event must have exactly 2 items, got {}: {}".format(
                        len(event_list), event_list)
                raise ValueError(msg)
            name, value = event_list
            value = self.event_object(name, value, timestamp)
            self.events.append(name)
            setattr(self, name, value)

        return


    class _EventObject(object):
        """ A class for ???
        
        """

        def __init__(self, name, value, timestamp):
            """ ??? """

            # ???
            if not isinstance(name, str):
                raise TypeError

            # ???
            self.name = name
            self.value = str(value) if value is not None else None
            self.timestamp = self._convert_time(timestamp)

        
        def _convert_time(self, tstamp):
            """ adds colon for local offset ... """

            try:
                timestamp = dateutil.parser.parse(tstamp).isoformat()
            except (TypeError, ValueError) as err:
                self.logger.error(msg)
                raise err(msg)
            return timestamp


if __name__ == "__main__":
    d = {"2018-05-08T12:07:34-0400": ["pst_converted", None],
         "2018-05-08T12:07:24-0400": ["pst_converter", "readpst"]}
    eo = EventsObject(d)
    #pass
