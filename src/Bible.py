
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
                return book.getChapterNames()
        return []

    def getBookByNum(self, num):
        for book in self.books:
            if book.number == num:
                return book
        return None

    def getVerses(self, bookName, chapters):
        for book in self.books:
            if book.bookName == bookName:
                return book.getVerses(chapters)

    def search(self, string):
        ret = []
        string = string.lower()
        for book in self.books:
            ret += book.search(string)
        return ret

    def search_chapters(self, string):
        copy = Bible()

        copy.translationName = self.translationName
        copy.translationAbbreviation = self.translationAbbreviation
        copy.translationInformation = self.translationInformation
        copy.language = self.language
        for book in self.books:
            ret = book.search_chapters(string)
            if ret is not None:
                copy.append(ret)
        return copy

    def sort(self):
        self.books.sort(key=lambda x: x.number)
        for book in self.books:
            book.sort()

    def next(self, current_book, chapter):
        found_next = False
        next_chapter = None
        found_next, next_chapter = current_book.next(chapter)
        if found_next:
            return found_next, current_book, next_chapter
        try:
            next_book_index = self.books.index(current_book) + 1

            if next_book_index < len(self.books):
                next_book = self.books[next_book_index]
                return True, next_book, next_book.chapters[0]
        except ValueError:
            return False, None, None
        return False, None, None

    def previous(self, current_book, chapter):
        found_previous = False
        previous_chapter = None
        found_previous, previous_chapter = current_book.previous(chapter)
        if found_previous:
            return found_previous, current_book, previous_chapter
        try:
            previous_book_index = self.books.index(current_book) - 1
            if previous_book_index >= 0:
                previous_book = self.books[previous_book_index]
                return True, previous_book, previous_book.chapters[len(
                    previous_book.chapters) - 1]
        except ValueError:
            return False, None, None
        return False, None, None


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
                chapter.addVerse(verse)
                found = True
                break
        if not found:
            c = Chapter(verse.chapter)
            c.addVerse(verse)
            self.chapters.append(c)

    def search(self, string):
        ret = []
        string = string.lower()
        for chapter in self.chapters:
            ret += chapter.search(string)
        return ret

    def search_chapters(self, string):
        copy = Book(self.bookName, self.number, self.shortName)
        for chapter in self.chapters:

            ret = chapter.search_chapters(string)
            if ret is not None:
                copy.addChapter(ret)
        if len(copy.chapters) > 0:
            return copy
        else:
            return None

    def getChapterNames(self):
        ret = []
        for chapter in self.chapters:
            ret.append(chapter.number)
        return ret

    def getVerses(self, thereChapters):
        for chapter in self.chapters:
            if chapter.number == thereChapters:
                return chapter.verses

    def getChapter(self, thereChapters):
        for chapter in self.chapters:
            if chapter.number == thereChapters:
                return chapter

    def sort(self):
        self.chapters.sort(key=lambda x: x.number)
        for chapter in self.chapters:
            chapter.sort()

    def next(self, current_chapter):
        next_chapter_index = self.chapters.index(current_chapter) + 1
        if next_chapter_index < len(self.chapters):
            next_chapter = self.chapters[next_chapter_index]
            return True, next_chapter
        return False, None

    def previous(self, current_chapter):
        previous_chapter_index = self.chapters.index(current_chapter) - 1
        if previous_chapter_index >= 0:
            previous_chapter = self.chapters[previous_chapter_index]
            return True, previous_chapter
        return False, None

def sort_verse(item):
    if type(item) == Verse:
        return item.verse * 2
    elif type(item) == Story:
        return item.verse * 2 - 1

class Chapter:
    def __init__(self, number=-1):
        self.number = number
        self.verses = []

    def __str__(self):
        return str(self.number)

    def addVerse(self, verse):
        self.verses.append(verse)

    def search(self, string):
        ret = []
        string = string.lower()
        for verse in self.verses:
            if string in verse.text.lower():
                ret.append(verse)
        return ret

    def search_chapters(self, string):
        ret = []
        string = string.lower()
        found_match = False
        for verse in self.verses:
            if string in verse.text.lower():
                found_match = True
                break
        if not found_match:
            return None
        copy = Chapter(self.number)
        for verse in self.verses:
            copy.addVerse(verse)
        return copy

    def sort(self):
        self.verses.sort(key=sort_verse)


class Verse:
    def __init__(self, bookNumber, chapter, verse, text):

        self.bookNumber = bookNumber
        self.chapter = chapter
        self.verse = verse
        self.text = text

    def getText(self):
        return self.text

    def __str__(self):
        return "Verse(" + str(self.bookNumber) + ", " + str(self.chapter) + \
            ", " + str(self.verse) + ", " + self.text + ")"


class Story:
    def __init__(self, bookNumber, chapter, verse, order, text):

        self.bookNumber = bookNumber
        self.chapter = chapter
        self.verse = verse
        self.text = text
        self.order = order

    def getText(self):
        return self.text

    def __str__(self):
        return "Story(" + str(self.bookNumber) + ", " + str(self.chapter) + \
            ", " + str(self.verse) + ", " + str(self.order) + ", " + self.text + ")"

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
