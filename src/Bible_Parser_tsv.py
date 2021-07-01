from .Bible import Book, Verse
from .Bible_Parser_Base import BibleParserBase
import os


class BibleParserTSV(BibleParserBase):
    name = "TSV"
    fileEndings = ["tsv"]
    def __init__(self, file_name):
        BibleParserBase.__init__(self, file_name)

    def loadInfo(self):

        with open(self.file_name) as myFile:
            lines = myFile.readlines()
            i = 0
            while i < len(lines):
                i += self.prosessVerseData(lines, i)
        self.bible.translationAbbreviation = os.path.basename(self.file_name)

    def loadAll(self):

        with open(self.file_name) as myFile:
            lines = myFile.readlines()
            i = 0
            while i < len(lines):
                i += self.prosessVerseData(lines, i)
        self.bible.translationAbbreviation = os.path.basename(self.file_name)

    def prosessVerseData(self, lines, index):
        data = lines[index].replace("\n", "").split('\t')
        if len(self.bible.getBooksChapterNames(data[0])) == 0:
            self.bible.append(Book(data[0], int(data[2]), data[1]))
        self.bible.addVerse(
            Verse(int(data[2]), int(data[3]), int(data[4]), data[5]))
        return 1
