from lxml import etree
import yaml

"""
todo:
    * test following a template call with another comment.
        - this SHOULD fail to replace.
    * ... with ANOTHER tempalte call!! haha
        - this SHOULD see only the last template as a real template.
    * add a type-check syntax: "x:str" and then check if the dict's value is the
    same type.
    * the 2nd line of the template should probably be a template ID for logging
    and debugging.
    * don't you need to make this recursive so that a templated element can exist
    as a child of another templated element? Or do we not need that in the real
    world?
        - actually, it looks like reading through all comments backwards works.
    * need to add support for namespace prefixes.
"""

### sample XML.
xdoc = """<premis>

<!-- Root level comments cannot be dependent on template calls.
Try it. I dare you.

e.g.
    <! - -
    TOMES_TEMPLATE: 0
    if_exists: [x,y]
    - - >
    <premis />
-->
<!--
TOMES_TEMPLATE: 1
if_exists: [x,y]
-->
<event>
    <!-- This event will only survive if its template call passes. -->
    <date>{x}</date>
    <!--
    TOMES_TEMPLATE: 1.5
    if_exists: [y]
    -->
    <time val="{y}" />
    <!--
    TOMES_TEMPLATE: 2
    if_exists: [zWon'tAppearBecauseThisKeyDoesn'tExist]
    -->
    <location id="{z}" />
</event>

<event>
    <!-- This event is not template dependent and will ALWAYS show. -->
    <date>{x}</date> <!-- User error: using a variable in a non-templated section. -->
    <time>foo</time>
</event>
</premis>"""
xtree = etree.fromstring(xdoc)

### beautifier per: http://blog.humaneguitarist.org/2011/11/12/pretty-printing-xml-with-python-lxml-and-xslt/
### ... because pretty_print gets wierd with line breaks and stuff.
def prettify(someXML):
  #for more on lxml/XSLT see: http://lxml.de/xpathxslt.html#xslt-result-objects
  xslt_tree = etree.fromstring("""
    <!-- XSLT taken from Comment 4 by Michael Kay found here:
    http://www.dpawson.co.uk/xsl/sect2/pretty.html#d8621e19 -->
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
      <xsl:strip-space elements="*"/>
      <xsl:template match="/">
        <xsl:copy-of select="."/>
      </xsl:template>
    </xsl:stylesheet>""")
  transform = etree.XSLT(xslt_tree)
  result = transform(someXML)
  return result


### Is the comment a template call?
def is_template_call(node):
    try:
        template = yaml.load(node.text.encode())
    except yaml.scanner.ScannerError as err:
        return False
    if isinstance(template, dict) \
       and "TOMES_TEMPLATE" in template \
       and type(node.getnext()).__name__ == "_Element":
            template_id = template["TOMES_TEMPLATE"]
            print("Found template with id: {}".format(template_id))
            return True
    else:
        return False


### Do the template tests all pass?
def call_template(node, gbs):

    report = []
    template = yaml.load(node.text.encode())

    try:
        for cond in template["if_exists"]:
            if cond in gbs:
                print("Found key: {}".format(cond))
                report.append(True)
            else:
                print("Missing key: {}".format(cond))
                report.append(False)
    except KeyError as err:
        return False

    if set(report) == {True}:
        passed = True
    else:
        passed = False
    return passed


### update XML per templating.
GBS = {"x":1,"y":2, "z":3}

def work():
    nodes = xtree.xpath("//comment()")
    for node in reversed(nodes):
        sib = node.getnext()
        parent = sib.getparent()
        if is_template_call(node):
            test = call_template(node,GBS)
            if test:
                new = etree.tostring(sib)
                new = new.decode().format(**GBS)
                new = etree.fromstring(new)
                parent.replace(sib, new)
            else:
                parent.remove(sib)
            node.text = None

work()
print("----------\n")
print(prettify(xtree))
    


