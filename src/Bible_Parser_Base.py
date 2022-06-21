from .Bible import *


class BibleParserBase:
    name = "Base"
    fileEndings = []

    def __init__(self, file_name):
        self.file_name = file_name
        self.bible = Bible()

    def isValidFileEnding(self, file_name):
        for ending in self.fileEndings:
            if '.' + ending in file_name:
                return True
        return False

    def getParserName(self):
        return self.name

    def getParserEndings(self):
        return self.fileEndings

    def loadAll(self):
        pass

    def loadInfo(self):
        pass


def check_extention(type_class, file_name):
    return type_class.isValidFileEnding(type_class, file_name)
