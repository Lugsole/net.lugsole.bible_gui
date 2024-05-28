from gi.repository import Gtk, Gio, Gst, Gdk, Pango, GLib, GObject
from gi.repository import Adw
from gettext import gettext as _

from .Bible import Verse, Story
from .mybible_to_markdown import convert_mybible_to_markdown, convert_mybible_to_text, has_tag, setBible,convert_mybible_to_text_buff
from .Bible_Parser import BibleParser, BibleParserSqLit3
from .tts import readText
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


Adw.init()


@Gtk.Template(resource_path='/net/lugsole/bible_gui/text_rendering.ui')
class BibleSettings(Adw.NavigationPage):
    __gtype_name__ = 'TextRendering'
    sub_header_bar = Gtk.Template.Child()
    play_button = Gtk.Template.Child()
    play_image = Gtk.Template.Child()
    previous_button = Gtk.Template.Child()
    next_button = Gtk.Template.Child()
    scrolled = Gtk.Template.Child()
    viewport = Gtk.Template.Child()
    bible_text = Gtk.Template.Child()
    Chapter = 0
    Book = 0

    def __init__(self):
        super().__init__()
        #print("init")
        self.Bible = None

    @GObject.Property(type=int)
    def chapter(self):
        return self.Chapter

    @chapter.setter
    def chapter(self, Chapter):
        self.Chapter = Chapter


    @GObject.Property(type=int)
    def book(self):
        return self.Book

    @book.setter
    def book(self, Book):
        self.Book = Book

    def setBible(self, b):
        self.Bible = b

    def setApp(self, app):
        self.App = app
        self.App.player.add_callback(self.done_playing)
        self.App.player.add_state_change_callback(self.update_play_icon)

    def UpdateTable(self, verses, title, p):
        if p is None:
            p = self.p
        setBible(self.Bible)
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
            book = self.Bible.getBookByNum(self.book)
            title = book.bookName.removesuffix('\u200e')
            + ' ' + str(self.chapter)
            print(book.bookName)
        print(title)
        text = Gtk.Label()
        if self.Bible.right_to_left:
            text.set_direction(Gtk.TextDirection.RTL)
        else:
            text.set_direction(Gtk.TextDirection.LTR)
        text.set_label(title)
        self.sub_header_bar.set_title_widget(text)


        read_text = ""
        use_md = False
        if isinstance(p, BibleParserSqLit3):
            for i in range(len(verses)):
                verse = verses[i]
                if has_tag(verse.text, "pb", i == 0):
                    use_md = True
                    break
        tb = Gtk.TextBuffer()
        title_props = {}
        title_props["scale"] = 1.5
        title_props["weight"] = Pango.Weight.BOLD
        tb.create_tag("Title", **title_props)
        tb.create_tag("h", **title_props) #, text_transform=Pango.TextTransform.CAPITALIZE)
        tb.create_tag("f", size=8*Pango.SCALE, rise=-6*Pango.SCALE, invisible=True)
        tb.create_tag("S", invisible=True)
        tb.create_tag("sup", scale=0.75, rise=4000)
        tb.create_tag("n", style=Pango.Style.OBLIQUE)
        tb.create_tag("e", style=Pango.Style.ITALIC)
        tb.create_tag("i", style=Pango.Style.OBLIQUE)
        tb.create_tag("t", style=Pango.Style.OBLIQUE, left_margin=20)
        tb.create_tag("J", foreground="Red",style=Pango.Style.OBLIQUE)
        tb.create_tag("underline", underline=Pango.Underline.SINGLE)
        for i in range(len(verses)):
            verse = verses[i]

            text_label = ""
            if not SameBook:
                text_label += self.Bible.getBookName(
                    verse.bookNumber).bookName + " "
            if not SameBook or not SameCh:
                text_label += str(verse.chapter) + ":"
            text_label += str(verse.verse)
            if isinstance(verse, Verse):
                if use_md and SameBook and SameCh:
                    convert_mybible_to_text_buff(verse.text, verse.verse, i == 0, True, tb, "Text")
                elif not use_md and isinstance(p, BibleParserSqLit3):

                    start, end = tb.get_bounds()
                    tb.insert(end, text_label + " " + \
                        convert_mybible_to_text(verse.text, None, True, True) + '\r')
                else:
                    start, end = tb.get_bounds()
                    tb.insert(end, text_label + " " + verse.text + '\r')
            elif isinstance(verse, Story):
                if 0 < i:
                    start, end = tb.get_bounds()
                    tb.insert(end, '\r')

                convert_mybible_to_text_buff(verse.text, None, True, True, tb, "Title")

            if isinstance(p, BibleParserSqLit3):
                read_text += convert_mybible_to_text(
                    verse.text, None, True, True) + ' '
            else:
                read_text += verse.text + ' '

        self.read_text = read_text

        self.bible_text.set_buffer(tb)


    @Gtk.Template.Callback()
    def next_chapter_cb(self, a):
        #GLib.idle_add(print,"Hello",priority=GLib.PRIORITY_HIGH_IDLE)
        self.next_action()

    def next_action(self):
        Found, book, chapter = self.Bible.getNextChapterByNum(self.Book,self.Chapter)
        if Found:
            self.Book = book.number
            self.Chapter = chapter.number
            self.UpdateTable(chapter.verses, None, None)
            status = self.App.player.get_status()
            self.App.player.end()
            self.update_prev_next()
            if status == "Playing":
                self.readChapter(None)
            else:
                self.update_play_icon()
            self.scrolled.set_vadjustment(None)

    def can_next(self):
        Found, book, chapter = self.Bible.getNextChapterByNum(self.Book, self.Chapter)
        return Found

    @Gtk.Template.Callback()
    def previous_chapter_cb(self, a):
        self.previous_action()

    def previous_action(self):
        Found, book, chapter = self.Bible.getPreviousChapterByNum(self.Book, self.Chapter)
        if Found:
            self.book = book.number
            self.chapter = chapter.number
            self.UpdateTable(chapter.verses, None, None)
            status = self.App.player.get_status()
            self.App.player.end()
            self.update_prev_next()
            if status == "Playing":
                self.readChapter(None)
            else:
                self.update_play_icon()
            self.scrolled.set_vadjustment(None)

    def can_previous(self):
        Found, book, chapter = self.Bible.getPreviousChapterByNum(self.Book, self.Chapter)
        return Found


    @Gtk.Template.Callback()
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

    def update_prev_next(self):
        self.next_button.set_sensitive(self.can_next())
        self.previous_button.set_sensitive(self.can_previous())

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
