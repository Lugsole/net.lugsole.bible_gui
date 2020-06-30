
class Bible:
    def __init__(self):
        self.translationName = ""
        self.translationAbbreviation = ""
        self.translationInformation = ""
        self.books = []
        self.language = ""

    def __str__(self):
        ret = ""

        ret += "translation name: " + self.translationName + '\n'
        ret += "translation abbreviation: " + self.translationAbbreviation + '\n'
        ret += "translation information: " + self.translationInformation + '\n'
        for book in self.books:
            ret += str(book) + '\n'
        return ret

    def append(self, book):
        self.books.append(book)

    def addVerse(self, verse):
        for book in self.books:
            if book.number == verse.bookNumber:
                # print(str(book))
                book.addVerse(verse)
                break

    def getBookNames(self):
        books = []
        for book in self.books:
            books.append(book.bookName)
        return books

    def getBookName(self, num):
        for book in self.books:
            if book.number == num:
                return book.bookName
        return ""

    def getBooksChapterNames(self, bookName):
        for book in self.books:
            if bookName == book.bookName:
                # print("getBooksChapterNames", "Good")
                return book.getChapterNames()
        return []

    def getVerses(self, bookName, chapters):
        # print("Finding", bookName)
        for book in self.books:
            if book.bookName == bookName:
                # print("Match book",str(book))
                return book.getVerses(chapters)
            # else:

                # print("No Match",str(book))

    def search(self, string):
        ret = []
        string = string.lower()
        for book in self.books:
            ret += book.search(string)
        # print(ret)
        return ret


class Book:
    def __init__(self, name, number=-1, shortName=""):

        self.bookName = name
        self.number = number
        self.shortName = shortName
        self.chapters = []

    def addChapter(self, chapter):
        self.chapters.append(chapter)

    def __str__(self):
        return self.bookName

    def addVerse(self, verse):
        found = False
        for chapter in self.chapters:
            if chapter.number == verse.chapter:
                # print("added Chapter")
                chapter.addVerse(verse)
                found = True
                break
        if not found:
            # print("New Chapter")
            c = Chapter(verse.chapter)
            c.addVerse(verse)
            self.chapters.append(c)

    def search(self, string):
        ret = []
        string = string.lower()
        for chapter in self.chapters:
            ret += chapter.search(string)
        return ret

    def getChapterNames(self):
        # print("getChapterNames","len", len(self.chapters))
        ret = []
        for chapter in self.chapters:
            ret.append(chapter.number)
        return ret

    def getVerses(self, thereChapters):
        for chapter in self.chapters:
            if chapter.number == thereChapters:
                return chapter.verses


class Chapter:
    def __init__(self, number=-1):
        self.number = number
        self.verses = []

    def addVerse(self, verse):
        self.verses.append(verse)

    def search(self, string):
        ret = []
        string = string.lower()
        for verse in self.verses:
            if string in verse.text.lower():
                ret.append(verse)
        # print(self.number,ret)
        return ret


class Verse:
    def __init__(self, bookNumber, chapter, verse, text):

        self.bookNumber = bookNumber
        self.chapter = chapter
        self.verse = verse
        self.text = text

    def getText(self):
        return self.text

    def __str__(self):
        return "Verse(" + str(self.bookNumber) + ", " + str(self.chapter) + ", " + str(self.verse) + ", " + self.text + ")"


class bibleSearchResults:
    def __init__(self):
        self.sameBookNumber = True
        self.sameChapter = True
        self.results = []

    def __add__(self, other):
        for result in other.results:
            self.add(result)

    def add(self, result):
        self.results.apped(result)
        if not result.bookNumber == self.results[0].bookNumber:
            self.sameBookNumber = False
        if not result.chapter == self.results[0].chapter:
            self.sameBookNumber = False
        if not result.verse == self.results[0].verse:
            self.sameBookNumber = False

