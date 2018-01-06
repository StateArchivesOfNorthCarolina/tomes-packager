from lxml import etree

"""
todo:
    - test following a template call with another comment.
        - this SHOULD fail to replace.
    - ... with ANOTHER tempalte call!! haha
        - this SHOULD see only the last template as a real template.
    - add a type-check syntax: "x:str" and then check if the dict's value is the
    same type.
    - the 2nd line of the template should probably be a template ID for logging
    and debugging.
    - don't you need to make this recursive so that a templated element can exist
    as a child of another templated element? Or do we not need that in the real
    world?
"""

### sample XML.
xdoc = """<premis>

<!-- Root level comments cannot be dependent on template calls.
Try it. I dare you.

e.g.
    <! - - TOMES_TEMPLATE_CALL
    x
    y
    - - >
    <premis />
-->
<!-- TOMES_TEMPLATE_CALL
x
y
-->
<event>
    <!-- This event will only survive if its template call passes. -->
    <date>{x}</date>
    <time>{y}</time>
    <!-- TOMES_TEMPLATE_CALL
    asdf
    -->
    <location id="{z}" />
</event>

<event>
    <!-- This event is not template dependent and will ALWAYS show. -->
    <date>{x}</date> <!-- User error: using a variable in a non templated section. -->
    <time>foo</time>
</event>
</premis>"""
xtree = etree.fromstring(xdoc)


### Is the comment a template call?
def is_template_call(c):
    br = c.text.find("\n") 
    if br == -1:
        return False
    elif c.text[:br].strip() == "TOMES_TEMPLATE_CALL" \
         and type(node.getnext()).__name__ == "_Element":
            return True
    else:
        return False


### Do the template tests all pass?
def call_template(x, gbs):
    " test conditions, return bool "

    report = []
    
    lines = node.text.split("\n")
    for line in lines[1:]:
        if line == "":
            continue
        if line.strip() in gbs:
            print("Found key: {}".format(line))
            report.append(True)
        else:
            print("Missing key: {}".format(line))
            report.append(False)

    if set(report) == {True}:
        passed = True
    else:
        passed = False
    return passed


### update XML per templating.
GBS = {"x":1,"y":2, "z":3}
nodes = xtree.xpath("comment()")
for node in nodes:
    ndx = xtree.index(node)
    sib = node.getnext()
    if is_template_call(node):
        test = call_template(node,GBS)
        if test:
            new = etree.tostring(sib)
            new = new.decode().format(**GBS)
            new = etree.fromstring(new)
            xtree.insert(ndx, new)
        xtree.remove(sib)
        xtree.remove(node)
        
print("----------\n")    
xdoc = etree.tostring(xtree, pretty_print=True)
print(xdoc.decode())
    


