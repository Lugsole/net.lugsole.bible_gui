

import gi

from .tts import readText
from .Bible_Parser import BibleParser
gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gio, Gst, Gdk
gi.require_version('Adw', '1')
from gi.repository import Adw
from .config import pkgdatadir, application_id, user_data_dir
import os
import time
Adw.init()



@Gtk.Template(resource_path='/net/lugsole/bible_gui/window.ui')
class BibleWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BibleWindow'

    myTable = Gtk.Template.Child()
    content_box = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()
    search = Gtk.Template.Child()
    right_box = Gtk.Template.Child()
    play_button = Gtk.Template.Child()
    play_image = Gtk.Template.Child()
    book_list = Gtk.Template.Child()
    previous_button = Gtk.Template.Child()
    next_button = Gtk.Template.Child()
    sub_header_bar = Gtk.Template.Child()
    scrolled = Gtk.Template.Child()
    viewport = Gtk.Template.Child()

    def __init__(self, App, **kwargs):
        super().__init__(**kwargs)
        self.App = App

        try:
            # try to connect to settings
            self.settings = Gio.Settings.new(self.App.BASE_KEY)
            base_file = self.settings.get_string("bible-translation")
            self.settings.connect(
                "changed::bible-translation",
                self.on_bible_translation_changed)
            full_path = os.path.join(user_data_dir, base_file)
            if base_file != "" and os.path.isfile(full_path):
                self.p = BibleParser(full_path)
            else:
                print("Falling back to KJV")
                self.p = BibleParser(os.path.join(pkgdatadir, "kjv.tsv"))
            self.p.loadAll()
        except Exception as e:
            print(e)
            print("Falling back to KJV")
            self.p = BibleParser(os.path.join(pkgdatadir, "kjv.tsv"))
            self.p.loadAll()
        self.origionalBible = self.p.bible
        self.Bible = self.origionalBible
        self.Bible.sort()

        self.search.connect(
            'search-changed', self.search_call
        )

        self.play_button.connect('clicked', self.readChapter)

        self.book = self.Bible.books[0]
        self.chapter = self.book.chapters[0]
        self.UpdateTable(self.chapter.verses)
        self.UpdateBooks()
        self.App.player.add_callback(self.done_playing)
        self.App.player.add_state_change_callback(self.update_play_icon)
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

            flowbox.insert(button,-1)
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
        if SameBook and SameCh:
            text = Gtk.Label()
            text.set_label( self.book.bookName + " - " + str(self.chapter.number))
            self.sub_header_bar.set_title_widget(text)
        i = 0
        for verse in verses:
            text_label = ""
            if not SameBook:
                text_label += self.Bible.getBookName(verse.bookNumber).bookName + " "

            if not SameBook or not SameCh:
                text_label += str(verse.chapter) + ":"
            text_label += str(verse.verse)

            verse_label = Gtk.Label()
            verse_label.set_label(text_label)
            verse_label.show()
            verse_label.set_xalign(0)
            verse_label.set_yalign(0)
            text = Gtk.Label()
            text.set_label(verse.text)
            text.show()
            text.set_wrap(True)
            text.set_xalign(0)

            self.myTable.insert_row(i)
            self.myTable.attach(verse_label, 0, i, 1, 1)
            self.myTable.attach(text, 1, i, 1, 1)
            i += 1

    @Gtk.Template.Callback()
    def back_clicked_cb(self, button):
        self.content_box.navigate(Adw.NavigationDirection.BACK)

    def search_call(self, b):
        search_term = self.search.get_text()
        if len(search_term) < 3:
            self.Bible = self.origionalBible
        else:
            filtered = self.origionalBible.search_chapters(search_term)
            self.Bible = filtered
        self.UpdateBooks()

    def show_page(self, button, page, book, chapter):
        if  self.chapter is not chapter:
            self.App.player.end()
            self.chapter = chapter
            self.book = book
            self.update_play_icon()
        verses = chapter.verses
        self.UpdateTable(verses)
        self.next_button.set_sensitive(self.can_next())
        self.previous_button.set_sensitive(self.can_previous())
        self.content_box.set_visible_child(page)
        self.scrolled.set_vadjustment(None)

    def readChapter(self, button):
        read = ""
        if  self.App.player.getstate() == Gst.State.PLAYING:
            self.App.player._pause()
        elif self.App.player.getstate() == Gst.State.PAUSED:
            self.App.player._play()
        else:
            for verse in self.chapter.verses:
                read += verse.text + " "
            self.App.player.start_file( readText(read, self.Bible.language))
            self.App.player.set_title(str(self.book) + " " + str(self.chapter))
            if self.Bible.translationName == '':
                self.App.player.set_artist([self.Bible.translationAbbreviation])
            else:
                self.App.player.set_artist([self.Bible.translationName])
            self.App.player.set_album(_("Bible"))
            self.App.player._play()
        self.update_play_icon()

    def done_playing(self):
        self.App.player.end()
        self.update_play_icon()

    def update_play_icon(self):
        action= "start"
        if self.App.player.getstate() == Gst.State.PLAYING:
            action= "pause"
        self.play_image.set_property("icon_name", "media-playback-"+action+"-symbolic")

    def on_bible_translation_changed(self, settings, key):
        base_file = settings.get_string("bible-translation")
        self.p = BibleParser(os.path.join(user_data_dir, base_file))
        self.p.loadAll()
        self.origionalBible = self.p.bible
        self.Bible = self.origionalBible
        self.Bible.sort()

        self.UpdateBooks()

    @Gtk.Template.Callback()
    def next_chapter_cb(self,a):
        self.next()

    def next(self):
        Found, book, chapter = self.Bible.next(self.book, self.chapter)
        if Found:
            self.book = book
            self.chapter = chapter
            self.UpdateTable(chapter.verses)
            status = self.App.player.get_status()
            self.App.player.end()
            self.next_button.set_sensitive(self.can_next())
            self.previous_button.set_sensitive(self.can_previous())
            if status == "Playing":
                self.readChapter(None)
            else:
                self.update_play_icon()
            self.scrolled.set_vadjustment(None)

    def can_next(self):
        Found, book, chapter = self.Bible.next(self.book, self.chapter)
        return Found

    @Gtk.Template.Callback()
    def previous_chapter_cb(self,a):
        self.previous()

    def previous(self):
        Found, book, chapter = self.Bible.previous(self.book, self.chapter)
        if Found:
            self.book = book
            self.chapter = chapter
            self.UpdateTable(chapter.verses)
            status = self.App.player.get_status()
            self.App.player.end()
            self.next_button.set_sensitive(self.can_next())
            self.previous_button.set_sensitive(self.can_previous())
            if status == "Playing":
                self.readChapter(None)
            else:
                self.update_play_icon()
            self.scrolled.set_vadjustment(None)

    def can_previous(self):
        Found, book, chapter = self.Bible.previous(self.book, self.chapter)
        return Found
