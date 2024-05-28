
string = "<pb/>In the <f>[2]</f>beginning <f>ⓐ</f>God created the heaven and the earth."
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser, ParseError
from xml.etree.ElementTree import Element,tostring

def convert(element):
    new_element = None
    if element.tag == "i":
        new_element = Element("span")
        new_element.attrib["style"] = "italic"
    elif element.tag == "J":
        new_element = Element("span")
        new_element.attrib["foreground"] = "red"
    elif element.tag == "text":
        new_element = Element("span")
    elif element.tag == "h":
        new_element = Element("span")
        new_element.attrib["size"] = "150%"
        new_element.attrib["weight"] = "bold"
    elif element.tag == "sup":
        new_element = Element("span")
        new_element.attrib["size"] = "75%"
        new_element.attrib["rise"] = "4000"
    elif element.tag == "S":
        if element.tail is not None:
            return element.tail
        else:
            return ""
    elif element.tag == "f":
        if element.tail is not None:
            return element.tail
        else:
            return ""
    elif element.tag == "br":
        if element.tail is not None:
            return "\r" + element.tail
        else:
            return "\r"
    elif element.tag == "pb":
        if element.tail is not None:
            return "\r" + element.tail
        else:
            return "\r"
    else:
        new_element = Element("span")
    new_element.tail = element.tail
    new_element.text = element.text
    for i in element:
        ret = convert(i)
        if isinstance(ret, Element) :
            new_element.append(ret)
        elif isinstance(ret, str):
            if len(new_element) == 0:
                if new_element.text is not None:
                    new_element.text += ret
                else:
                    new_element.text = ret
            else:
                if new_element[-1].tail is not None:
                    new_element[-1].tail += ret
                else:
                    new_element[-1].tail = ret
    return new_element
bible = None
def setBible(bible_in):
    global bible
    bible = bible_in

def has_tag(text, tag, some_bool):

    try:
        parser = XMLParser()
        text = "<text>"+string+"</text>"
        element = ET.fromstring(text, parser=parser)
    except ParseError:
        return False
    ret = element.findall(".//"+tag)
    return len(ret) > 0
def convert_mybible_to_markdown(
        string,
        verse_number,
        remove_pre_whitespace,
        remove_post_whitespace):
    try:
        parser = XMLParser()
        text = "<text>"+string+"</text>"
        element = ET.fromstring(text, parser=parser)
    except ParseError:
        return ''
    if verse_number is not None:
        new_element = Element("sup")
        new_element.text = str(verse_number)
        new_element.tail = element.text
        if isinstance(new_element, Element) :
            element.insert(0, new_element)
    new_root = convert(element)
    return tostring(new_root, encoding='unicode')
def convert_mybible_to_text(
        string,
        verse_number,
        remove_pre_whitespace,
        remove_post_whitespace):
    try:
        parser = XMLParser()
        text = "<text>"+string+"</text>"
        element = ET.fromstring(text, parser=parser)
    except ParseError:
        return ''
    new_root = convert(element)
    return tostring(new_root, encoding='unicode', method='text')


print(convert_mybible_to_markdown('<pb/><e><h>A song of degrees, or Psalm of David.</h></e> <pb/></n><br/> <pb/>If the Lord had not been <f>[1]</f>on our side, (may Israel now say)',None, False,False))
