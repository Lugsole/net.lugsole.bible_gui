from .Bible import Book, Verse
from .Bible_Parser_Base import BibleParserBase


class BibleParserSPB(BibleParserBase):
    name = "spb"
    fileEndings = ["spb"]
    book = 0
    chapter = 0
    verse = 0

    def __init__(self, file_name):
        BibleParserBase.__init__(self, file_name)

    def loadInfo(self):
        with open(self.file_name) as myFile:
            lines = []
            for line in myFile:
                if line.startswith("--"):
                    break
                lines.append(line)
            i = 0
            while i < len(lines) and not lines[i].startswith("--"):
                i += self.prosessData(lines, i)
        self.bible.translationName = os.path.basename(self.file_name)

    def loadAll(self):

        with open(self.file_name) as myFile:
            lines = myFile.readlines()
            i = 0
            while i < len(lines) and not lines[i].startswith("--"):

                i += self.prosessData(lines, i)
            i += 1
            while i < len(lines):
                i += self.prosessVerseData(lines, i)

    def prosessData(self, lines, index):
        line = lines[index].replace("\n", '')
        parts = line.split('\t')
        if line.startswith("##Title:"):
            self.bible.translationName = parts[1]
            return 1
        elif line.startswith("##Abbreviation:"):
            self.bible.translationAbbreviation = parts[1]
            return 1
        elif line.startswith("##Information:"):
            self.bible.translationInformation = parts[1].replace("@%", '\n')
            return 1
        elif line.startswith("##RightToLeft:"):
            offset = 1
            while index + offset < len(lines) and not(
                lines[index + offset].startswith("##") or
                lines[index + offset].startswith("--")
            ):
                line = lines[index + offset]
                parts = line.split('\t')
                self.bible.append(Book(parts[1], int(parts[0])))
                offset += 1
            return offset

        else:
            return 1

    def prosessVerseData(self, lines, index):
        data = lines[index].split('\t')
        if len(data) == 5:
            self.bible.addVerse(
                Verse(int(data[1]),
                      int(data[2]),
                      int(data[3]),
                      data[4].rstrip()))
            if not(
                (self.verse +
                 1 == int(
                     data[3]) and self.chapter == int(
                     data[2]) and self.book == int(
                     data[1])) or (
                    1 == int(
                        data[3]) and self.chapter +
                    1 == int(
                        data[2]) and self.book == int(
                        data[1])) or (
                    1 == int(
                        data[3]) and (
                        1 == int(
                            data[2]) or 0 == int(
                            data[2])) and self.book +
                    1 == int(
                        data[1]))):
                print(
                    "Unusual transition:",
                    self.book,
                    self.chapter,
                    self.verse)
            self.book = int(data[1])
            self.chapter = int(data[2])
            self.verse = int(data[3])
        else:
            print("Bad line", data)
        return 1
