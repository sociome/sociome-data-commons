'''metadata.py has a number of subroutines that render the metadata standard in different ways
'''
import xml.etree.ElementTree as ET

data_type_enum = ['string', 'num', 'date', 'url']
data_documentation_enum = {1:'Database', 2:'Table', 3:''}

def depth_iter(element, tag=None):
    '''dept_iter recursively iterates through an xml tree.
    '''
    stack = []
    stack.append(iter([element]))
    while stack:
        e = next(stack[-1], None)
        if e == None:
            stack.pop()
        else:
            stack.append(iter(e))
            if tag == None or e.tag == tag:
                yield (e, len(stack) - 1)


def do_html(path):
    lines = []
    e = ET.parse(path + "/core.xml")
    for element, level in depth_iter(e.getroot()):

        name = str(element.text).strip() + ' ' + data_documentation_enum[level]

        header = '<h'+str(level*2)+'>' + ' ' + str(element.tag) + ': ' + str(name) + '</h'+str(level*2)+'>'

        lines.append('<div class="content" style="padding-left: %spx;">' % (str(15*(level-1))))
        lines.append(header)
        lines.append(element.attrib['description'])

        if str(element.tag) == 'attribute':
            reference_file = element.attrib['compileType']

            if element.attrib.get('cardinality', '') == 'many':
                lines.append("<p>This attribute can have a set of values.</p>")

            if reference_file in data_type_enum:
                lines.append("<p>This attribute is a "+ reference_file +" field.</p>")
                lines.append('</div>')
                continue

            lines.append("<p>This attribute is populated with the following values:</p>")

            ref_e = ET.parse(path + '/' + reference_file + '.xml')

            for ref_element, ref_level in depth_iter(ref_e.getroot()):

                if ref_element.attrib.get('name', '') == name.strip():
                    for child in (ref_element):
                        lines.append('<p>-' + '<b>'+child.text+"</b>: " + child.attrib.get('description',"") + "</p>")

        lines.append('</div>')

    return '\n'.join(lines)


def do_form(path):
    lines = []
    e = ET.parse(path + "/core.xml")
    for element, level in depth_iter(e.getroot()):

        name = str(element.text).strip() + ' ' + data_documentation_enum[level]
        name = name.strip()

        if level != 3:
            continue

        
        toggle = "<a onclick='$(\"#%s\").toggle();'>Add: %s</a><br/>" % (name, name)

        lines.append(toggle)
        lines.append('<div id="%s" style="display: none;">' % (name))
        lines.append('<span style="font-size: 10px;">%s</span><br/>' % (element.attrib['description']))

        if str(element.tag) == 'attribute':
            reference_file = element.attrib['compileType']

            if reference_file in data_type_enum:
                lines.append("<input type='text' name='%s'>" % name)
            else:
                lines.append('<select id="%sinp" name="%s">' % (name, name))

                ref_e = ET.parse(path + '/' + reference_file + '.xml')

                for ref_element, ref_level in depth_iter(ref_e.getroot()):

                    if ref_element.attrib.get('name', '') == name.strip():
                        for child in (ref_element):
                            lines.append('<option value="%s">%s</option>' % (child.text, child.text))

                lines.append('</select>')

        lines.append('</div><br/>')

    return '\n'.join(lines)