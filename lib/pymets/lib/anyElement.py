#!/usr/bin/env python3

""" The module contain a class to create any METS element with optional attributes. """

# import modules.
import logging
import logging.config
from lxml import etree


class AnyElement():
    """ A class to create any METS element with optional attributes. """
    

    def __init__(self, ns_prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map


    def anyElement(self, name, attributes=None):
        """ Creates an element @name with optional attributes.

        Args:
            - name (str): The name of the element to create.
            - attributes (dict): The optional attributes to set. Attribute namespace prefixes
            are supported if the prefix is registered (i.e. a key) in the instance's @ns_map.
        
        Returns:
            lxml.etree._Element: The return value.

        Raises:
            KeyError: If an unregister namespace prefix is used.
        """

        self.logger.info("Creating <{}> element.".format(name))

        # supported namespace prefixes for elements (e.g. "mets:fileSec").
        if ":" in name:
            pref, name = name.split(":")
            self.logger.info("Found namespace prefix '{}' for <{}> element.".format(pref, 
                name))
            try:
                any_el = "{" + self.ns_map[pref] + "}" + name
            except KeyError as err:
                self.logger.warning("Namespace prefix '{}' is not registered.".format(pref))
                self.logger.error(err)
                raise err
        else:
            pref, name = self.ns_prefix, name
            
        # create @name element.
        any_el = etree.Element("{" + self.ns_map[pref] + "}" + name, nsmap=self.ns_map)
        
        # set optional attributes.
        if attributes is not None:
            
            self.logger.info("Appending attributes to <{}> element.".format(name))
            for attribute, value in attributes.items():
                
                # supported namespace prefixes for attributes (e.g. "mets:ID").
                if ":" in attribute:
                    pref, attr = attribute.split(":")
                    self.logger.info("Found namespace prefix '{}' for <{}> element.".format(
                        pref, name))
                    try:
                        attribute = "{" + self.ns_map[pref] + "}" + attr
                    except KeyError as err:
                        self.logger.warning("Namespace prefix '{}' is not registered.".format(
                            pref))
                        self.logger.error(err)
                        raise err

                self.logger.info("Setting attribute '{}' with value '{}'.".format(attribute,
                    value))     
                any_el.set(attribute, value)

        return any_el


if __name__ == "__main__":
    pass

