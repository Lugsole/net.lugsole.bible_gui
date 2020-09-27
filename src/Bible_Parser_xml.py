from .Bible import Book, Verse
from .Bible_Parser_Base import BibleParserBase
import xml.etree.cElementTree as ET
import os.path

class BibleParserXML(BibleParserBase):
    name = "XML"
    fileEndings = ["xml"]

    def __init__(self, file_name):
        BibleParserBase.__init__(self, file_name)

    def loadInfo(self):
        self.bible.translationAbbreviation = os.path.basename(self.file_name)
        self.bible.translationName = os.path.basename(self.file_name)

    def loadAll(self):
        tree = ET.ElementTree(file=self.file_name)
        root = tree.getroot()
        books = root.getchildren()
        for book in books:
            chapters = book.getchildren()
            b_number = int(book.attrib["bnumber"])
            self.bible.append(Book(book.attrib["bname"], b_number))

            for chapter in chapters:
                ch_number = chapter.attrib["cnumber"]
                verses = chapter.getchildren()
                for verse in verses:
                    v_number = verse.attrib["vnumber"]
                    self.bible.addVerse(
                        Verse(b_number, ch_number, v_number, verse.text))
