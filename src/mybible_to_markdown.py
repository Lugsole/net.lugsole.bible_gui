

bible = None
def setBible(bible_in):
    global bible
    bible = bible_in

class tag_renderer:
    def __init__(self, tag_name, pre_tag, post_tag):
        self.pre_tag = pre_tag
        self.post_tag = post_tag
        self.clear_format = False
        self.tag_name = tag_name

    def convert_to_markdown(self, tag):
        ret = ""
        for i in tag.children:
            ret += i.convert_to_markdown()
        return self.pre_tag + ret + self.post_tag

    def convert_to_text(self, tag):
        ret = ""
        for i in tag.children:
            ret += i.convert_to_markdown()
        return ret


class one_tag_renderer:
    def __init__(self, tag_name, ret_tag, ret_text):
        self.ret_tag = ret_tag
        self.ret_text = ret_text
        self.clear_format = False
        self.tag_name = tag_name

    def convert_to_markdown(self, tag):
        return self.ret_tag

    def convert_to_text(self, tag):
        return self.ret_text


class tag_renderer_clear:
    def __init__(self, tag_name, pre_tag, post_tag):
        self.pre_tag = pre_tag
        self.post_tag = post_tag
        self.clear_format = True
        self.tag_name = tag_name

    def convert_to_markdown(self, tag):
        ret = ""
        for i in tag.children:
            ret += i.convert_to_markdown()
        return self.pre_tag + ret + self.post_tag

    def convert_to_text(self, tag):
        ret = ""
        for i in tag.children:
            ret += i.convert_to_markdown()
        return ret


class x_tag_parser:
    def __init__(self):
        self.clear_format = True
        self.tag_name = 'x'

    def convert_to_markdown(self, tag):
        global bible
        ret = ""
        for i in tag.children:
            ret += i.convert_to_markdown()
        verse = ret.split(" ",1)
        num = int(verse[0])
        book = ""
        if bible is not None:
            book = bible.getBookName(num)
        return '<span underline="single">' + book + " " + verse[1] + '</span>'

    def convert_to_text(self, tag):
        global bible
        ret = ""
        for i in tag.children:
            ret += i.convert_to_markdown()
        verse = ret.split(" ",1)
        num = int(verse[0])
        book = ""
        if bible is not None:
            book = bible.getBookName(num)
        return book + " " + verse[1]

usable_tags = {
    'pb': one_tag_renderer('pb', '\r', '\r'),
    'br': one_tag_renderer('br', '\r', '\r'),
    'f': one_tag_renderer('f', '', ''),
    't': tag_renderer('t', '<i>', '</i>\r'),
    'J': tag_renderer('J', '<span foreground="red">', '</span>'),
    'n': tag_renderer('n', '', ''),
    'Text': tag_renderer_clear('Text', '', ''),
    'Title': tag_renderer_clear('Title', '<span size="150%"><b>', '</b></span>'),
    'i': tag_renderer('i', '<i>', '</i>'),
    'e': tag_renderer('e', '<b>', '</b>'),
    'sup': tag_renderer('sup', '<span rise="4000" size="75%">', '</span> '),
    'S': one_tag_renderer('S', '', ''),
    'h': tag_renderer_clear('h', '<span size="150%"><b>', '</b></span>'),
    'x': x_tag_parser(),
}


class text:
    def __init__(self, text):
        self.text = text

    def convert_to_markdown(self):
        return self.text

    def convert_to_text(self):
        return self.text

    def is_whitespace(self):
        return self.text.isspace()


class tag:
    def __init__(self, tag_name):
        self.tag = tag_name
        self.children = []

    def add_sub_tag(self, child):
        self.children.append(child)

    def convert_to_markdown(self):
        if self.tag in usable_tags:
            return usable_tags[self.tag].convert_to_markdown(self)
        else:
            print("un known tag", self.tag)
            return ""

    def convert_to_text(self):
        if self.tag in usable_tags:
            return usable_tags[self.tag].convert_to_text(self)
        else:
            print("un known tag", self.tag)
            return ""

    def is_whitespace(self):
        return self.tag == "pb" or self.tag == "br" or self.tag not in usable_tags

    def has_tag(self, string):

        #print(self.tag, string)
        if self.tag == string:
            return True
        for i in self.children:
            #print(isinstance(i, tag) and i.has_tag(string))
            if isinstance(i, tag) and i.has_tag(string):
                return True
        return False


class root:
    def __init__(self):
        self.children = []
        self.tag = "text"

    def add_sub_tag(self, child):
        self.children.append(child)

    def __str__(self):
        return "The amount of children are: " + str(len(self.children))

    def convert_to_markdown(self):
        ret = ""
        for i in self.children:
            ret += i.convert_to_markdown()
        return ret

    def convert_to_text(self):
        ret = ""
        for i in self.children:
            ret += i.convert_to_text()
        return ret

    def remove_pre(self):
        while self.children[0].is_whitespace():
            del self.children[0]

    def insert_number(self, verse_number):
        i = 0
        while i < len(self.children) and self.children[i].is_whitespace():
            i += 1
        new_tag = tag("sup")
        new_tag.add_sub_tag(text(str(verse_number)))
        self.children.insert(i, new_tag)

    def has_tag(self, string):
        for i in self.children:
            # print(i)
            #print(isinstance(i, tag) and i.has_tag(string))
            if isinstance(i, tag) and i.has_tag(string):
                return True

        return False


def parse_text_tags(string, parent):
    children = []
    while string is not None and len(string) > 0:
        if '<' == string[0]:
            # print("if")
            if '/' == string[1]:
                #print("closing tag")
                return string
            #print("new tag")
            # print(parse_tag(string))
            # return
            string, nothing = parse_tag(string)
            parent.add_sub_tag(nothing)
        else:
            # print("Parse_String")
            string, nothing = parse_string(string)
            parent.add_sub_tag(nothing)
    return string


def parse_string(string):
    new_string = ""
    while len(string) > 0:
        #print("String char", string[0])
        if '<' == string[0]:
            #print("String", new_string)
            return string, text(new_string)
        else:
            #print("string else", string[0])
            new_string += string[0]
            string = string[1:]
    #print("String", new_string)
    return string, text(new_string)


def parse_tag(string):
    string = string[1:]
    tag_name = ""
    closed = False
    while string is not None:
        if '>' == string[0]:
            string = string[1:]
            break
        elif '/' == string[0] and '>' == string[1]:
            string = string[2:]
            closed = True
            break

        else:
            tag_name += string[0]
            string = string[1:]
    #print("Tag Name: ", tag_name)
    new_tag = tag(tag_name)
    if closed:
        #print("self closed tag")
        return (string, new_tag)
    string = parse_text_tags(string, new_tag)
    #print("Almost Done")
    # print(string[:2])
    if string is None:
        return (string, new_tag)

    string = string[2:]
    tag_name = ""
    while string is not None and len(string) > 0:
        if '>' == string[0]:
            #print("Closing tag Name: ", tag_name)
            return (string[1:], new_tag)
        else:
            tag_name += string[0]
            string = string[1:]
    #print("Closing tag Name: ", tag_name)
    return (string, new_tag)

def get_all_tags(tb,tags):

    apply_tags = []
    for tag_name in reversed(tags):
        if tb.get_tag_table().lookup(tag_name) is not None:
            apply_tags.append(tag_name)
        if tag_name in ["Title","Text","n"]:
            break
    return apply_tags

def tree_to_text_buff(tb, tags, tree):
    tags = tags[:]
    tags.append(tree.tag)
    for i in tree.children:
        if isinstance(i, tag):
            if i.tag == "br"  or i.tag == "pb":
                start, end = tb.get_bounds()
                tb.insert(end, '\r')
            elif i.tag == "x":
                ret = ""
                for ii in i.children:
                    ret += ii.convert_to_text()
                verse = ret.split(" ",1)
                num = int(verse[0])
                book = ""
                if bible is not None:
                    book = bible.getBookName(num)
                apply_tags = get_all_tags(tb,tags)
                verse_text = book + " " + verse[1]
                #print(apply_tags, verse_text)
                start, end = tb.get_bounds()
                apply_tags.append("underline")
                tb.insert_with_tags_by_name(end, verse_text, *apply_tags)
                #return '<span underline="single">' + book + " " + verse[1] + '</span>'
            elif i.tag == "sup":
                start, end = tb.get_bounds()
                tb.insert(end, ' ')
                tree_to_text_buff(tb,tags,i)
                start, end = tb.get_bounds()
                tb.insert(end, ' ')
            else:
                tree_to_text_buff(tb,tags,i)
        if isinstance(i, text):
            apply_tags = get_all_tags(tb,tags)
            #print(apply_tags, i.text)
            start, end = tb.get_bounds()
            tb.insert_with_tags_by_name(end, i.text, *apply_tags)
        #print(i)

def convert_mybible_to_text_buff(
        string,
        verse_number,
        remove_pre_whitespace,
        remove_post_whitespace,
        tb,
        root_tag_name):
    r = root()
    while string is not None and len(string) != 0:
        string = parse_text_tags(string, r)
        if string is not None and len(string) != 0:
            string = string.split(">",1)[1]
    if remove_pre_whitespace:
        r.remove_pre()
    if verse_number is not None:
        r.insert_number(verse_number)
    r.tag = root_tag_name
    #print_tree(r)
    textbuff = tree_to_text_buff(tb,[],r)
    #print(text)
    return textbuff

def convert_mybible_to_markdown(
        string,
        verse_number,
        remove_pre_whitespace,
        remove_post_whitespace):
    r = root()
    while string is not None and len(string) != 0:
        string = parse_text_tags(string, r)
        if string is not None and len(string) != 0:
            string = string.split(">",1)[1]
    if remove_pre_whitespace:
        r.remove_pre()
    if verse_number is not None:
        r.insert_number(verse_number)
    #print_tree(r)
    text = r.convert_to_markdown()
    #print(text)
    return text


def convert_mybible_to_text(
        string,
        verse_number,
        remove_pre_whitespace,
        remove_post_whitespace):
    r = root()
    while string is not None and len(string) != 0:
        string = parse_text_tags(string, r)
        if string is not None and len(string) != 0:
            string = string.split(">",1)[1]
    if remove_pre_whitespace:
        r.remove_pre()
    if verse_number is not None:
        r.insert_number(verse_number)
    return r.convert_to_text()


def has_tag(string, text_tag, remove_pre_whitespace):
    r = root()
    while string is not None and len(string) != 0:
        string = parse_text_tags(string, r)
        if string is not None and len(string) != 0:
            string = string.split(">",1)[1]
    if remove_pre_whitespace:
        r.remove_pre()
    return r.has_tag(text_tag)


def print_tree(tree,depth=""):
    print(depth, isinstance(tree,tag))
    print(depth, isinstance(tree,root))
    if isinstance(tree,root):
        print(depth, 'ROOT')
    if isinstance(tree,tag):
        print(depth, tree.tag)
    if isinstance(tree,tag) or isinstance(tree,root):
        for i in tree.children:
            print_tree(i, depth + '\t')


