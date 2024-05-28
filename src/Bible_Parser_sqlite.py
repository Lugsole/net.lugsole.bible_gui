from .Bible import Book, Verse, Story
import sqlite3
import re
from .Bible_Parser_Base import BibleParserBase


class BibleParserSqLit3(BibleParserBase):
    name = "SQLite/My Bible"
    fileEndings = ["SQLite3", "sqlite"]

    def __init__(self, file_name):
        BibleParserBase.__init__(self, file_name)

    def isValidFileEnding(self, filename):
        return '.sqlite3' in filename.lower() and '.commentaries.sqlite3' not in filename.lower(
        ) and '.dictionary.sqlite3' not in filename.lower() and '.crossreferences.sqlite3' not in filename.lower()

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


        t = ('right_to_left',)
        c.execute('SELECT name, value FROM info where name=?', t)
        txt = c.fetchone()
        if txt is not None and txt[1] is not None:
            self.bible.right_to_left = txt[1].upper() == "TRUE"
            #print(self.bible.right_to_left)

        for row in c.execute(
                'SELECT long_name,book_number,short_name FROM books'):
            self.bible.append(
                Book(row[0].strip(), number=int(row[1]), shortName=row[2]))

        conn.close()

    def loadAll(self):
        self.loadInfo()
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        for row in c.execute(
                'SELECT book_number, chapter, verse, text FROM verses'):
            verseText = row[3].rstrip()
            verseText = verseText.replace('¶', '')
            self.bible.addVerse(
                Verse(int(row[0]), int(row[1]), int(row[2]), verseText))
        c = conn.cursor()

        listOfTables = c.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
          AND name='stories'; """).fetchall()

        if listOfTables != []:
            #print('stories table found!')
            c = conn.cursor()
            has_order_if_several = False
            for row in c.execute("PRAGMA table_info('stories')").fetchall():
                if row[1] == 'order_if_several':
                    has_order_if_several = True
            if has_order_if_several:
                for row in c.execute(
                        'select book_number, chapter, verse, order_if_several, title from stories'):
                    verseText = row[4].rstrip()

                    s = Story(int(row[0]), int(row[1]), int(
                        row[2]), int(row[3]), verseText)
                    self.bible.addVerse(s)
            else:
                for row in c.execute(
                        'select book_number, chapter, verse, title from stories'):
                    verseText = row[3].rstrip()

                    s = Story(int(row[0]), int(row[1]), int(
                        row[2]), 0, verseText)
                    self.bible.addVerse(s)
        else:
            print('stories table NOT found!')

        conn.close()

