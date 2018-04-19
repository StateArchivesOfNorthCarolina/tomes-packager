""" ???

Todo:
    * Verify template is a file on __init__.
        - And verify base is a folder.
"""


# import modules.
import glob
import jinja2
import os
from datetime import datetime
from lib.file_to_object import FileToObject


class Packager():


    def __init__(self, base, template, charset="utf-8"):
        """ ??? """

        # set attributes.
        self.base = base
        self.template = template
        self.charset = charset

        # ???
        self.f2o = FileToObject
        self.xsd = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + 
                "/lib/mets_1-11.xsd")


    def get_data(self):
        """ ??? """

        # get padding length for local file identifiers.
        get_pad_len = lambda x: len(str(len(x))) + 1
        get_id = lambda x,y: str(y.index(x)).zfill(get_pad_len(y))
        
        # ???
        data = {}
        root_files = glob.glob(self.base + "/*.*")
        data[""] = [self.f2o(f, root=self.base, index=get_id(f, root_files)) for f in 
                root_files]

        # ???
        folders = [f for f in glob.glob(self.base + "/*/")]
        for folder in folders:
            files = [f for f in glob.glob(folder + "/**", recursive=True) 
                    if os.path.isfile(f)]
            folder = os.path.relpath(folder, start=self.base)
            data[folder] = [self.f2o(f, root=self.base, index=get_id(f, files)) for f in files]

        return data


    def render_template(self, *args, **kwargs):
        """ Loads an @xml string after formatting the string using the
        string.Formatter.format() with for *args and **kwargs.
        ??? now using jinja2 so update ???
        
        Args:
            - *args/**kwargs: The optional arguments to pass to the string formatter.
            
        Returns:
            lxml.etree._Element: The return value.
        """

        # ??
        with open(self.template, encoding=self.charset) as tf:
                xml = tf.read()
        template = jinja2.Template(xml)
        rendered_template = template.render(*args, **kwargs)
        
        # load string as etree._Element.
        template_el = rendered_template#self.load(rendered_template, is_raw=True)
        return template_el


    def validate_mets(self, xdoc):
        """ Validates @xdoc file against @self.xsd.
        
        Args:
            - xdoc (str): The etree._Element to validate.
            
        Returns:
            bool: The return value. True for valid, otherwise False.
        """
        
        # load XSD.
        xsd = self.load(self.xsd_file, False)
        validator = etree.XMLSchema(xsd)
        
        # validate.
        is_valid = validator.validate(xdoc)
        return is_valid


if __name__ == "__main__":

    p = Packager(".", "../mets_templates/test.xml")
    data = p.get_data()
    #for d in data:
    #    print(d)
    #print(p.xsd)
    open(p.xsd)
    docs = [(x.name, x.checksum) for x in data["lib"]]
    #print(docs)
    t = p.render_template(mets_ctime=datetime.now().isoformat(), assets=data)
    print(t)