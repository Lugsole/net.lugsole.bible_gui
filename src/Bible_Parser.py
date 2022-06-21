from .Bible_Parser_spb import BibleParserSPB
from .Bible_Parser_sqlite import BibleParserSqLit3
from .Bible_Parser_tsv import BibleParserTSV
from .Bible_Parser_xml import BibleParserXML
from .Bible_Parser_Base import check_extention

allParsers = [
    BibleParserSPB,
    BibleParserSqLit3,
    BibleParserTSV,
    BibleParserXML]


def BibleParser(filename):
    for file_type in allParsers:
        if check_extention(file_type, filename):
            return file_type(filename)
