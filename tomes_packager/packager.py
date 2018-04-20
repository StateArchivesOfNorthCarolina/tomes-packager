""" ???

Todo:
    * Verify template is a file on __init__.
        - And verify base is a folder.
    * Need to determine constant vars.
        - ISO/UTC now.
        - What else?
    * Need self.data and self.data_folders (list of folder names only).
        - i.e. more side effect!
"""


# import modules.
import glob
import jinja2
import os
from datetime import datetime
from lxml import etree
from lib.directory_object import DirectoryObject
from lib.file_object import FileObject


    
class Packager():


    def __init__(self, base, template, charset="utf-8"):
        """ ??? """

        # set attributes.
        self.base = base
        self.template = template
        self.charset = charset

        # ???
        self.directory_object = DirectoryObject
        self.file_object = FileObject
        self.xsd_file = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + 
                "/lib/mets_1-11.xsd")
        self.beautifier = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + 
                "/lib/beautifier.xsl")


    class __DirectoryList(list):
        """ ??? """

        def __getattr__(self, att):
            """ ??? """
            
            try:
                names = [d.name for d in self]
                found = names.index(att)
                files = [f.name for f in self[found].files]
                return files
            except ValueError:
                return None

        def __contains__(self, test):
            """ ??? """
            return True if test in [d.name for d in self] else False


    def load_event_data(self):
        """ ??? """
        # raise error is key value is not a time; convert to UTC.


    def get_data(self):
        """ ??? """

        # get padding length for local file identifiers.
        get_pad_len = lambda x: 1 + len(str(len(x)))
        get_id = lambda x, y: str(y.index(x)).zfill(get_pad_len(y))
        
        # ???
        data = self.__DirectoryList()

        # ???
        root_files = glob.glob(self.base + "/*.*")
        root_files = [self.file_object(f, root=self.base, index=get_id(f, root_files)) for f in 
                root_files]
        root = self.directory_object(self.base, "_", root_files)
        data.append(root)

        # ???
        folders = [f for f in glob.glob(self.base + "/*/")]
        for folder in folders:
            files = [f for f in glob.glob(folder + "/**", recursive=True) if 
                    os.path.isfile(f)]
            files = [self.file_object(f, root=self.base, index=get_id(f, files)) for f in files]
            rel_folder = os.path.relpath(folder, start=self.base)
            folder = self.directory_object(folder, rel_folder, files)
            data.append(folder)

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
        template = jinja2.Template(xml, trim_blocks=True, lstrip_blocks=True, 
                block_start_string="%%", block_end_string="%%",
                comment_start_string="<!--#", comment_end_string="#-->")
        rendered_template = template.render(*args, **kwargs)
        
        # load string as etree._Element. ??? string yes?
        template_el = rendered_template#self.load(rendered_template, is_raw=True)
        return template_el


    def beautify_mets(self, mets):
      """ ??? """

      beautifier = etree.parse(self.beautifier)
      transform = etree.XSLT(beautifier)
      result = transform(mets)

      return mets
    

    def validate_mets(self, mets):
        """ Validates @mets file against @self.xsd.
        
        Args:
            - xdoc (str): The etree._Element to validate.
            
        Returns:
            bool: The return value. True for valid, otherwise False.
        """
        
        # load XSD.
        xsd = etree.parse(self.xsd_file)
        validator = etree.XMLSchema(xsd)
        
        # validate.
        is_valid = validator.validate(mets)
        return is_valid


if __name__ == "__main__":

    p = Packager(".", "../mets_templates/test.xml")
    data = p.get_data()
    #for d in data:
    #    print(d)
    #    print(d.name)
    #print(p.xsd)
    #docs = [(x.name, x.checksum) for x in data[0].files]
    #print(docs)
    t = p.render_template(mets_ctime=datetime.utcnow().isoformat()+"Z", folders=data)
    t = etree.fromstring(t)
    valid = " It is {} that this METS is valid. ".format(p.validate_mets(t))
    t.append(etree.Comment(valid))
    t = p.beautify_mets(t)
    t = etree.tostring(t, pretty_print=True).decode()
    print(t)
