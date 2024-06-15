
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
gi.require_version('Adw', '1')

from .Bible import Verse, Story
from .path_order import find_file_on_path, walk_files_on_path
from .mybible_to_markdown import convert_mybible_to_markdown, convert_mybible_to_text, has_tag, setBible,convert_mybible_to_text_buff
from .Bible_Parser import BibleParser, BibleParserSqLit3
from .tts import readText
from gi.repository import Gtk, Gio, Gst, Gdk, Pango, GLib
from gi.repository import Adw
from .config import pkgdatadir, application_id, user_data_dir, translationdir, default_translation
from .text_rendering import BibleSettings
import os
import time
from gettext import gettext as _
import locale


Adw.init()



@Gtk.Template(resource_path='/net/lugsole/bible_gui/window.ui')
class BibleWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BibleWindow'

    content_box = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()
    search = Gtk.Template.Child()
    right_box = Gtk.Template.Child()
    book_list = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    tr = Gtk.Template.Child()

    def __init__(self, App, **kwargs):
        super().__init__(**kwargs)
        self.App = App
        # print(find_file_on_path("kjv.tsv"))
        # print(walk_files_on_path())
        # print(default_translation)
        try:
            # try to connect to settings
            self.settings = Gio.Settings.new(self.App.BASE_KEY)
            base_file = self.settings.get_string("bible-translation")
            #base_file = "French_LouisSegond.spb"
            self.settings.connect(
                "changed::bible-translation",
                self.on_bible_translation_changed)
            full_path = os.path.join(find_file_on_path(base_file), base_file)
            #print(full_path)
            if base_file != "" and os.path.isfile(full_path):
                self.p = BibleParser(full_path)
            else:
                print("Falling back to KJV")
                base_file = default_translation
                full_path = os.path.join(
                    find_file_on_path(base_file), base_file)
                self.p = BibleParser(full_path)
            self.p.loadAll()
        except Exception as e:
            print(e)
            print("Falling back to KJV")
            base_file = default_translation
            full_path = os.path.join(find_file_on_path(base_file), base_file)
            self.p = BibleParser(full_path)
            self.p.loadAll()
        self.origionalBible = self.p.bible
        self.Bible = self.origionalBible
        self.Bible.sort()

        self.search.connect(
            'search-changed', self.search_call
        )


        self.book = self.Bible.books[0]
        self.chapter = self.book.chapters[0]
        self.tr.setBible(self.Bible)
        self.tr.p = self.p
        self.tr.setApp(self.App)
        self.tr.book = self.book.number
        self.tr.chapter = self.chapter.number
        self.tr.UpdateTable(self.chapter.verses, None, self.p)
        self.tr.update_prev_next()
        self.UpdateBooks()
        self.show()

    def add_book(self, Bible, book, chapters):
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(30)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.show()
        for chapter in chapters:
            button = Gtk.Button(label=str(chapter.number))
            button.show()
            button.connect(
                'clicked',
                self.show_page,
                self.right_box,
                book, chapter)

            flowbox.insert(button, -1)
        expand = Adw.ExpanderRow()
        expand.set_property("title", book.bookName)

        expand.add_row(flowbox)
        expand.show()
        self.book_list.append(expand)

    def UpdateBooks(self):
        while self.book_list.get_row_at_index(0) is not None:
            self.book_list.remove(self.book_list.get_row_at_index(0))
        for book in self.Bible.books:
            chapters = book.chapters
            self.add_book(self.Bible, book, chapters)

    def search_call(self, b):
        search_term = self.search.get_text()
        if len(search_term) < 3:
            self.Bible = self.origionalBible
        else:
            filtered = self.origionalBible.search_chapters(search_term)
            self.Bible = filtered
        self.UpdateBooks()

    def show_page(self, button, page, book, chapter):
        if self.chapter is not chapter:
            self.App.player.end()
            self.chapter = chapter
            self.book = book
            self.update_play_icon()
        verses = chapter.verses
        self.tr.book = book.number
        self.tr.chapter = chapter.number
        self.tr.UpdateTable(verses, None, self.p)
        self.tr.update_prev_next()
        self.split_view.set_show_content(True)

    def set_chapter(self, book_number, chapter_number):
        #print("set_chapter", book_number, chapter_number)

        self.book = self.Bible.getBookByNum(book_number)
        self.chapter = self.book.getChapter(chapter_number)

    def readChapter(self, button):
        read = ""
        if self.App.player.getstate() == Gst.State.PLAYING:
            self.App.player._pause()
        elif self.App.player.getstate() == Gst.State.PAUSED:
            self.App.player._play()
        else:
            self.App.player.start_file(
                readText(
                    self.read_text,
                    self.Bible.language))
            self.App.player.set_title(str(self.book) + " " + str(self.chapter))
            if self.Bible.translationName == '':
                self.App.player.set_artist(
                    [self.Bible.translationAbbreviation])
            else:
                self.App.player.set_artist([self.Bible.translationName])
            self.App.player.set_album(_("Bible"))
            self.App.player._play()
        self.update_play_icon()

    def done_playing(self):
        self.App.player.end()
        self.update_play_icon()

    def update_play_icon(self):
        action = "start"
        if self.App.player.getstate() == Gst.State.PLAYING:
            action = "pause"

    def on_bible_translation_changed(self, settings, key):
        base_file = settings.get_string("bible-translation")
        #print("Loading new file")
        if base_file == "":
            base_file = default_translation
            full_path = os.path.join(find_file_on_path(base_file), base_file)
            self.p = BibleParser(full_path)
        else:
            full_path = os.path.join(find_file_on_path(base_file), base_file)
            self.p = BibleParser(full_path)
        #print("File loaded", find_file_on_path(base_file))
        self.p.loadAll()
        self.origionalBible = self.p.bible
        self.Bible = self.origionalBible
        self.Bible.sort()

        self.UpdateBooks()

        self.book = self.Bible.books[0]
        self.chapter = self.book.chapters[0]
        self.tr.book = self.book.number
        self.tr.chapter = self.chapter.number
        self.tr.setBible(self.Bible)
        self.tr.p = self.p
        self.tr.UpdateTable(self.chapter.verses, None, self.p)
        self.tr.update_prev_next()

