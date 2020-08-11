from .Bible import Book, Verse
import sqlite3
import re
from .Bible_Parser_Base import BibleParserBase


class BibleParserSqLit3(BibleParserBase):
    def __init__(self, file_name):
        BibleParserBase.__init__(self, file_name)

    def loadInfo(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        t = ('detailed_info',)
        c.execute('SELECT name, value FROM info where name=?', t)
        txt = c.fetchone()
        if txt is not None and txt[1] is not None:
            self.bible.translationInformation = txt[1]
        t = ('description',)
        c.execute('SELECT name, value FROM info where name=?', t)
        txt = c.fetchone()
        if txt is not None or txt[1] is not None:
            self.bible.translationName = txt[1]
        t = ('language',)
        c.execute('SELECT name, value FROM info where name=?', t)
        txt = c.fetchone()
        if txt is not None and txt[1] is not None:
            self.bible.language = txt[1]
        for row in c.execute('SELECT long_name,book_number,short_name FROM books'):
            self.bible.append(
                Book(row[0], number=int(row[1]), shortName=row[2]))

        conn.close()

    def loadAll(self):
        self.loadInfo()
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        for row in c.execute('SELECT book_number, chapter, verse, text FROM verses'):
            verseText = row[3].rstrip()
            verseText = re.sub(
               r"\<(?<=\<)(.*?)(?=\>)\>",
               "",
               verseText
            )
            self.bible.addVerse(
                Verse(int(row[0]), int(row[1]), int(row[2]), verseText))
        conn.close()

