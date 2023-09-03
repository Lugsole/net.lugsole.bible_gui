import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
gi.require_version('Adw', '1')


from gettext import gettext as _
import time
import os
from .config import pkgdatadir, application_id, user_data_dir, translationdir, default_translation
from gi.repository import Adw
from gi.repository import Gtk, Gio, Gst, Gdk
import gi

from .tts import readText
from .Bible_Parser import BibleParser, BibleParserSqLit3
from .mybible_to_markdown import convert_mybible_to_markdown, convert_mybible_to_text, has_tag
from .path_order import find_file_on_path, walk_files_on_path
from .Bible import Verse, Story

Adw.init()


@Gtk.Template(resource_path='/net/lugsole/bible_gui/window.ui')
class BibleWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BibleWindow'

    bible_text = Gtk.Template.Child()
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
        #print(find_file_on_path("kjv.tsv"))
        #print(walk_files_on_path())
        #print(default_translation)
        try:
            # try to connect to settings
            self.settings = Gio.Settings.new(self.App.BASE_KEY)
            base_file = self.settings.get_string("bible-translation")
            self.settings.connect(
                "changed::bible-translation",
                self.on_bible_translation_changed)
            full_path = os.path.join(find_file_on_path(base_file),base_file)
            if base_file != "" and os.path.isfile(full_path):
                self.p = BibleParser(full_path)
            else:
                print("Falling back to KJV")
                base_file = default_translation
                full_path = os.path.join(find_file_on_path(base_file),base_file)
                self.p = BibleParser(full_path)
            self.p.loadAll()
        except Exception as e:
            print(e)
            print("Falling back to KJV")
            base_file = default_translation
            full_path = os.path.join(find_file_on_path(base_file),base_file)
            self.p = BibleParser(full_path)
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
        self.UpdateTable(self.chapter.verses, None)
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

    def UpdateTable(self, verses, title):
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
        if title is None:
            title = self.book.bookName + " - " + str(self.chapter.number)

        text = Gtk.Label()
        text.set_label(title)
        self.sub_header_bar.set_title_widget(text)

        text = ""
        read_text = ""
        use_md = False
        if isinstance(self.p, BibleParserSqLit3):
            for i in range(len(verses)):
                verse = verses[i]
                if has_tag(verse.text, "pb", i == 0):
                    use_md = True
                    break

        for i in range(len(verses)):
            verse = verses[i]

            text_label = ""
            if not SameBook:
                text_label += self.Bible.getBookName(
                    verse.bookNumber).bookName + " "
            if not SameBook or not SameCh:
                text_label += str(verse.chapter) + ":"
            text_label += str(verse.verse)
            if type (verse) == Verse:
                if use_md and SameBook and SameCh:
                    text += convert_mybible_to_markdown(verse.text, verse.verse, i == 0, False) + " "
                elif not use_md and  isinstance(self.p, BibleParserSqLit3):
                    text += text_label + " " + convert_mybible_to_text(verse.text, None, True, True) + '\r'
                else:
                    text += text_label + " " + verse.text + '\r'
            elif type (verse) == Story:
                if 0 < i:
                    text += "\r"
                text += convert_mybible_to_markdown(verse.text, None, True, True)

            if isinstance(self.p, BibleParserSqLit3):
                read_text += convert_mybible_to_text(verse.text, None, True, True) + ' '
            else:
                read_text += verse.text + ' '

        self.read_text = read_text

        buff = self.bible_text.get_buffer()
        buff.begin_irreversible_action()
        start,end = buff.get_bounds()
        buff.delete(start,end)
        start_it = buff.get_start_iter()
        if use_md or isinstance(self.p, BibleParserSqLit3):
            buff.insert_markup(start_it, text, -1)
        else:
            buff.insert(start_it, text, -1)

        buff.end_irreversible_action()

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
        if self.chapter is not chapter:
            self.App.player.end()
            self.chapter = chapter
            self.book = book
            self.update_play_icon()
        verses = chapter.verses
        self.UpdateTable(verses, None)
        self.next_button.set_sensitive(self.can_next())
        self.previous_button.set_sensitive(self.can_previous())
        self.content_box.set_visible_child(page)
        self.scrolled.set_vadjustment(None)

    def set_chapter(self, book_number, chapter_number):
        print("set_chapter", book_number, chapter_number)

        self.book = self.Bible.getBookByNum(book_number)
        self.chapter = self.book.getChapter(chapter_number)

    def readChapter(self, button):
        read = ""
        if self.App.player.getstate() == Gst.State.PLAYING:
            self.App.player._pause()
        elif self.App.player.getstate() == Gst.State.PAUSED:
            self.App.player._play()
        else:
            self.App.player.start_file(readText(self.read_text, self.Bible.language))
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
        self.play_image.set_property(
            "icon_name",
            "media-playback-" +
            action +
            "-symbolic")

    def on_bible_translation_changed(self, settings, key):
        base_file = settings.get_string("bible-translation")
        #print("Loading new file")
        if base_file == "":
                base_file = default_translation
                full_path = os.path.join(find_file_on_path(base_file),base_file)
                self.p = BibleParser(full_path)
        else:
            full_path = os.path.join(find_file_on_path(base_file),base_file)
            self.p = BibleParser(full_path)
        #print("File loaded", find_file_on_path(base_file))
        self.p.loadAll()
        self.origionalBible = self.p.bible
        self.Bible = self.origionalBible
        self.Bible.sort()

        self.UpdateBooks()

        self.book = self.Bible.books[0]
        self.chapter = self.book.chapters[0]
        self.UpdateTable(self.chapter.verses, None)

    @Gtk.Template.Callback()
    def next_chapter_cb(self, a):
        self.next()

    def next(self):
        Found, book, chapter = self.Bible.next(self.book, self.chapter)
        if Found:
            self.book = book
            self.chapter = chapter
            self.UpdateTable(chapter.verses, None)
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
    def previous_chapter_cb(self, a):
        self.previous()

    def previous(self):
        Found, book, chapter = self.Bible.previous(self.book, self.chapter)
        if Found:
            self.book = book
            self.chapter = chapter
            self.UpdateTable(chapter.verses, None)
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
