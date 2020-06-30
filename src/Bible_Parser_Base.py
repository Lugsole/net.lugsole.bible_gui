from .Bible import *


class BibleParserBase:
    def __init__(self, file_name):
        self.file_name = file_name
        self.bible = Bible()

    def loadAll(self):
        pass

    def loadInfo(self):
        pass
