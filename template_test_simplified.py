import yaml
from lxml import etree

"""
Todo:
    * add support for attributes and multiple attributes:
        <foo FILL="..." ATTRIBUTES="[{'at1':'{a}', 'at2':'{b}foo'}, Comment.]" />
    * create template/YAML parser function.
    * create element update/replace function.
    * check for yaml.scanner.ScannerError, etc.
"""

# XML snippet with TOMES_* attribute markup.
# could be METS or anything else; i.e. code should be namespace agnostic.
xdoc = """<?xml version="1.0" encoding="UTF-8"?>
<mets:mets xmlns:mets="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation=
    "http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/version111/mets.xsd">
    <mets:metsHdr/>
    <mets:amdSec ID="amdSec_1">
    <mets:techMD ID="techMD_1" TOMES_TEMPLATE="[{'a': 1, 'b': True}, Nice to comment here 
    because unlike an XML comment this will get removed.]">
        <mets:mdWrap MDTYPE="PREMIS:OBJECT">
            <mets:xmlData>
                <premis:premis xmlns:premis="http://www.loc.gov/premis/v3" version="3.0" 
                xsi:schemaLocation="http://www.loc.gov/premis/v3 premis.xsd">
                    <premis:object xsi:type="premis:representation">
                        <premis:objectIdentifier>
                            <premis:objectIdentifierType 
                            valueURI="http://id.loc.gov/vocabulary/identifiers/local">
                            local</premis:objectIdentifierType>
                            <premis:objectIdentifierValue
                            TOMES_TEMPLATE_FILL="Anything goes, such as comments that will
                            get deleted VS an XML comment.">{a}-{b} is the value I seek!
                            </premis:objectIdentifierValue>
                        </premis:objectIdentifier>
                        <premis:significantProperties>
                            <premis:significantPropertiesValue>
                            </premis:significantPropertiesValue>
                        </premis:significantProperties>
                    </premis:object>
                </premis:premis>
            </mets:xmlData>
        </mets:mdWrap>
    </mets:techMD>
</mets:amdSec>
<mets:structMap>
<mets:div/>
</mets:structMap>
</mets:mets>"""

# establish template attributes and XPATHs.
template_signifier = "TOMES_TEMPLATE" 
template_fill = "TOMES_TEMPLATE_FILL" # pymets constructor will eventually take TEMPLATE and
                                      # FILL attribute names.
sig_path = "//*[@{}]".format(template_signifier)
fill_path = "//*[@{}]".format(template_fill)

# these are the events that will be passed in.
events = {"a": 1, "b": True, "c": False}

# parse @xdoc.
root = etree.fromstring(xdoc.encode())
for el in root.xpath(sig_path):

    # parse template.
    atts = dict(el.items())
    atts = yaml.load(atts[template_signifier])
    atts = atts[0] # item 1: conditions; optional item 2: comment.

    # do the conditions match what's in @events?
    tests = []
    for att in atts:
        if att in events and atts[att] == events[att]:
            tests.append(True)
        else:
            tests.append(False)
    test = False not in tests

    # if test failed, remove element and continue.
    if not test:
        el.getparent().remove(el)
        continue

    # replace element: add all children and attributes (sans template signifier).
    new = etree.Element(el.tag)
    for k, v in el.items():
        if k != template_signifier:
            new.set(k,v)
    for child in el:
        new.append(child)

    # find FILL attributes and format child element text.
    for cel in new.xpath(fill_path):
        
        # parse template: does this look familiar? Move this into a function.
        atts = dict(el.items())
        atts = yaml.load(atts[template_signifier])
        atts = atts[0] # item 1: conditions; optional item 2: comment.
        
        # format child text.
        cel.text = cel.text.format(**atts)
            # needs to be TRY/EXCEPT w/ KeyError; also check that text is not None.

        # replace child with new element (sans template fill).
        newcel = etree.Element(cel.tag)
        for k, v in cel.items():
            if k != template_fill:
                newcel.set(k,v)
        newcel.text = cel.text
        # for subchild in cel: # shouldn't be needed because FILL elements should have no 
                               # children right?
        #    newcel.append(subchild)
        cel.getparent().replace(cel, newcel)
    el.getparent().replace(el, new)
        

# get XML string again.
xdoc = etree.tostring(root, pretty_print=True).decode()

# validate but exempt xsi:type validatation that libxml2 can't handle.
# this is due to PREMIS design issue (IMO).
##xsd = etree.XMLSchema(etree.parse("mets_1-11.xsd"))
##try:
##    xsd.assertValid(root)
##except etree.DocumentInvalid as err:
##    if "xsi:type attribute" not in err.args[0]:
##        raise err

        

