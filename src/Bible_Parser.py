from .Bible_Parser_spb import  BibleParserSPB
from .Bible_Parser_sqlite import BibleParserSqLit3
from .Bible_Parser_tsv import BibleParserTSV

def BibleParser(filename):
    if '.spb' in filename.lower():
        return BibleParserSPB(filename)
    elif '.sqlite3' in filename.lower() and not '.commentaries.sqlite3' in filename.lower() and not '.dictionary.sqlite3' in filename.lower()and not '.crossreferences.sqlite3' in filename.lower():
        return BibleParserSqLit3(filename)
    elif '.tsv' in filename.lower():
        return BibleParserTSV(filename)
