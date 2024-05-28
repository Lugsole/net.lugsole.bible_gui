from .Bible import Book, Verse
from .Bible_Parser_Base import BibleParserBase
import xml.etree.ElementTree as ET
import os.path


data = ["Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Songs",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation"]

class BibleParserXML(BibleParserBase):
    name = "XML"
    fileEndings = ["xml"]

    def __init__(self, file_name):
        BibleParserBase.__init__(self, file_name)

    def loadInfo(self):
        self.bible.translationAbbreviation = os.path.basename(self.file_name)
        self.bible.translationName = os.path.basename(self.file_name)
        tree = ET.ElementTree(file=self.file_name)
        root = tree.getroot()
        if "biblename" in root.attrib:
            self.bible.translationName = root.attrib['biblename']
        for info_data in root.iter('INFORMATION'):
            #print("info_data", info_data)
            for info_data_sub in info_data:
                #print("info_data_sub", info_data_sub)
                #print("info_data_sub.tag", info_data_sub.tag)
                #print("info_data_sub.text", info_data_sub.text)
                if info_data_sub.tag == "identifier":
                    self.bible.translationAbbreviation = info_data_sub.text
                elif info_data_sub.tag == "title":
                    self.bible.translationName = info_data_sub.text
                elif info_data_sub.tag == "description":
                    self.bible.translationInformation = info_data_sub.text

    def loadAll(self):
        tree = ET.ElementTree(file=self.file_name)
        books = tree.getroot()
        #print(len(data))
        for book in books.iter('BIBLEBOOK'):
            b_number = int(book.attrib["bnumber"])
            b_name = None
            if "bname" in book.attrib:
                b_name =    book.attrib["bname"]
            if b_name is None:
                b_name = data[b_number-1]
            self.bible.append(Book(b_name, b_number))

            for chapter in book:
                ch_number = int(chapter.attrib["cnumber"])
                for verse in chapter:
                    v_number = int(verse.attrib["vnumber"])
                    self.bible.addVerse(
                        Verse(b_number, ch_number, v_number, str(ET.tostring(verse, encoding="unicode", method="text")).strip()))
