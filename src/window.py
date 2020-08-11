

import gi

from .tts import readText
from .settings import BibleSettings
from .Bible_Parser import BibleParser
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import GObject, GLib, Gtk, Gio, Gst
gi.require_version('Handy', '1')
from gi.repository import Handy
from .config import pkgdatadir
import os



@Gtk.Template(resource_path='/net/lugsole/bible_gui/window.ui')
class BibleWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'BibleWindow'

    BASE_KEY = "net.lugsole.bible_gui"

    myTable = Gtk.Template.Child()
    header_box = Gtk.Template.Child()
    content_box = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()
    search = Gtk.Template.Child()
    scrolled_window = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    play_button = Gtk.Template.Child()
    play_image = Gtk.Template.Child()
    book_list = Gtk.Template.Child()

    def __init__(self, App, **kwargs):
        super().__init__(**kwargs)
        self.App = App

        try:
            # try to connect to settings
            self.settings = Gio.Settings.new(self.BASE_KEY)
            base_file = self.settings.get_string("bible-translation")
            self.settings.connect(
                "changed::bible-translation",
                self.on_bible_translation_changed)
            if base_file != "":
                self.p = BibleParser(
                    os.path.join(GLib.get_user_data_dir(), base_file))
            else:
                self.p = BibleParser(os.path.join(pkgdatadir, "kjv.tsv"))
        except Exception:
            try_file = os.path.join(GLib.get_user_data_dir(), "main.SQLite3")
            if os.path.isfile(try_file):
                self.p = BibleParser(try_file)
            else:
                self.p = BibleParser(os.path.join(pkgdatadir, "kjv.tsv"))
        self.p.loadAll()
        self.Bible = self.p.bible

        self.search.connect(
            'key-press-event', self.search_call
        )

        self.back_button.connect('clicked', self.show_page_back, self.sidebar)
        self.play_button.connect('clicked', self.readChapter)
        action_print = Gio.SimpleAction.new("preferences", None)
        action_print.connect("activate", self.launch_settings)
        App.add_action(action_print)
        self.book = ""
        self.chapter = ""

        self.UpdateBooks()
        first_book = self.Bible.getBookNames()[0]
        first_chapter = self.Bible.getBooksChapterNames(first_book)[0]
        verses = self.Bible.getVerses(first_book, first_chapter)
        self.UpdateTable(verses)

        self.player = None

    def add_book(self, name, chapters):
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(30)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.show()
        for chapter in chapters:
            button = Gtk.Button(name, label=chapter)
            button.show()
            button.connect(
                'clicked',
                self.show_page,
                self.scrolled_window,
                name, chapter)

            flowbox.add(button)
        expand = Handy.ExpanderRow()
        expand.set_property("title", name)

        expand.add(flowbox)
        expand.show()
        self.book_list.add(expand)

    def UpdateBooks(self):
        for item in self.book_list.get_children():
            self.book_list.remove(item)
        books = self.Bible.getBookNames()
        for book in books:
            chapters = self.Bible.getBooksChapterNames(book)
            self.add_book(book, chapters)

    def UpdateTable(self, verses):
        while(self.myTable.get_child_at(0, 0) is not None):
            self.myTable.remove_row(0)

        if len(verses) <= 0:
            return
        chNum = verses[0].chapter
        bookNum = verses[0].bookNumber
        SameCh = True
        SameBook = True
        for verse in verses:
            if verse.chapter != chNum:
                SameCh = False
            if verse.bookNumber != bookNum:
                SameBook = False
                break
        i = 0
        for verse in verses:
            text_label = ""
            if not SameBook:
                text_label += self.Bible.getBookName(verse.bookNumber) + " "

            if not SameBook or not SameCh:
                text_label += str(verse.chapter) + ":"
            text_label += str(verse.verse)

            verse_label = Gtk.Label(text_label)
            verse_label.show()
            verse_label.set_xalign(0)
            verse_label.set_yalign(0)
            text = Gtk.Label(verse.text)
            text.show()
            text.set_line_wrap(True)
            text.set_xalign(0)

            self.myTable.insert_row(i)
            self.myTable.attach(verse_label, 0, i, 1, 1)
            self.myTable.attach(text, 1, i, 1, 1)
            i += 1

    def show_page_back(self, button, page):
        self.content_box.set_visible_child(page)

    def search_call(self, a, b):
        if b.get_keyval().keyval == 65293:
            verses = self.Bible.search(a.get_text())
            self.UpdateTable(verses)
            self.content_box.set_visible_child(self.scrolled_window)

    def show_page(self, button, page, book, chapter):
        self.book = book
        self.chapter = chapter
        if self.player is not None:
            self.player.end()
            self.update_play_icon()
        self.player = None
        verses = self.Bible.getVerses(book, chapter)
        self.UpdateTable(verses)
        self.content_box.set_visible_child(page)

    def readChapter(self, button):
        verses = self.Bible.getVerses(self.book, self.chapter)
        read = ""
        if self.player is not None and self.player.getstate() == Gst.State.PLAYING:
            self.player.Pause()
        elif self.player is not None and self.player.getstate() == Gst.State.PAUSED:
            self.player.Play()
        else:
            for verse in verses:
                read += verse.text + " "
            self.player = readText(read, self.Bible.language)
            self.player.add_callback(self.done_playing)
            self.player.Play()
        self.update_play_icon()

    def done_playing(self):
        self.player.end()
        self.player = None
        self.update_play_icon()

    def update_play_icon(self):
        action= "start"
        if self.player is not None and self.player.getstate() == Gst.State.PLAYING:
            action= "pause"
        self.play_image.set_property("icon_name", "media-playback-"+action+"-symbolic")

    def launch_settings(self, e1, e2):
        BibleSettings(self.App, self.BASE_KEY)

    def on_bible_translation_changed(self, settings, key):
        base_file = settings.get_string("bible-translation")
        self.p = BibleParser(os.path.join(GLib.get_user_data_dir(), base_file))
        self.p.loadAll()
        self.Bible = self.p.bible

        self.UpdateBooks()
