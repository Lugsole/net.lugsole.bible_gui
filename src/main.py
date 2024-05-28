
import sys

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')

from gi.repository import Adw, Gtk, Gio, GLib
from .window import BibleWindow
from .Audio_Player import Player
from .config import application_id, VERSION
from .settings import BibleSettings
from gettext import gettext as _


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=application_id,
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.props.resource_base_path = "/net/lugsole/bible_gui"

        self.BASE_KEY = application_id
        GLib.set_application_name(_("Bible"))
        GLib.set_prgname(application_id)
        GLib.setenv("PULSE_PROP_media.role", "music", True)
        self.player = Player(self)
        action_print = Gio.SimpleAction.new("preferences", None)
        action_print.connect("activate", self.launch_settings)
        self.add_action(action_print)
        action_print = Gio.SimpleAction.new("about", None)
        action_print.connect("activate", self.show_about)
        self.add_action(action_print)
        #print("init ended")

    def do_activate(self):
        # print("activate")
        self._window = self.props.active_window
        if not self._window:
            self._window = BibleWindow(self, application=self)
        self._window.present()

        if self.props.application_id == "net.lugsole.bible_gui.Devel":
            self._window.get_style_context().add_class('devel')

    def do_open(self, a1, a2, a3):
        # print("open")
        # print(self)
        # print(a1)
        # print(a2)
        # print(a3)
        # print(dir(a1[0]))

        self._window = self.props.active_window
        if not self._window:
            self._window = BibleWindow(self, application=self)
        self._window.present()

        if self.props.application_id == "net.lugsole.bible_gui.Devel":
            self._window.get_style_context().add_class('devel')

        for i in range(len(a1)):
            print("get_basename", a1[i].get_basename())
            #print("get_child", a1[i].get_child())
            #print("get_child_for_display_name", a1[i].get_child_for_display_name())
            #print("get_data", a1[i].get_data())
            print("get_parent", a1[i].get_parent())
            print("get_parse_name", a1[i].get_parse_name())
            print("get_path", a1[i].get_path())
            #print("get_properties", a1[i].get_properties())
            #print("get_property", a1[i].get_property())
            #print("get_qdata", a1[i].get_qdata())
            #print("get_relative_path", a1[i].get_relative_path())
            print("get_uri", a1[i].get_uri())
            print("get_uri_scheme", a1[i].get_uri_scheme())
            #print("getv", a1[i].getv())
            self.parse(a1[i].get_basename())

    def raide_main_window(self):
        self._window.present()

    def launch_settings(self, e1, e2):
        #print(e1)
        #print(e2)
        settings = BibleSettings(self)
        if self.props.application_id == "net.lugsole.bible_gui.Devel":
            settings.get_style_context().add_class('devel')
        settings.set_transient_for(self._window)

    def show_about(self, e1, e2):
        dialog = Adw.AboutWindow()
        if self.props.application_id == "net.lugsole.bible_gui.Devel":
            dialog.get_style_context().add_class('devel')
        dialog.set_transient_for(self._window)
        dialog.set_application_name(_("Bible"))
        dialog.set_website("https://lugsole.net/programs/bible")
        dialog.set_copyright("Copyright © 2020-2023 Lugsole")
        dialog.set_version(VERSION)
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_developers(["Lugsole"])
        dialog.set_application_icon(application_id)
        dialog.show()

    def parse(self, books_chapter):
        t1 = books_chapter.split(' ', 1)
        book_number = int(t1[0])
        print("book_number", book_number)
        rest = t1[1]
        start_chapter_str = ''
        while len(rest) > 0 and '0' <= rest[0] and '9' >= rest[0]:
            # print(rest[0])
            start_chapter_str += rest[0]
            rest = rest[1:]
        start_chapter_number = int(start_chapter_str)
        print("start_chapter_number", start_chapter_number)
        if 0 == len(rest):
            print("Done, no more")
            self._window.set_chapter(book_number, start_chapter_number)
            self._window.UpdateTable(self._window.chapter.verses, None)
            self._window.content_box.set_visible_child(self._window.right_box)
        elif rest[0] == ':':
            print("parsing verse")
            start_verse_str = ''
            rest = rest[1:]
            while len(rest) > 0 and '0' <= rest[0] and '9' >= rest[0]:
                # print(rest[0])
                start_verse_str += rest[0]
                rest = rest[1:]
            start_verse_number = int(start_verse_str)
            print("start_verse_number", start_verse_number)
            if 0 == len(rest):
                print("Done, no more")
                self._window.set_chapter(book_number, start_chapter_number)
                self._window.UpdateTable(
                    list(
                        filter(
                            lambda x: (
                                x.verse == start_verse_number),
                            self._window.chapter.verses)),
                    None)
                self._window.content_box.set_visible_child(
                    self._window.right_box)
            elif rest[0] == '-':
                print("parsing verse")
                next_str = ''
                rest = rest[1:]
                while len(rest) > 0 and '0' <= rest[0] and '9' >= rest[0]:
                    # print(rest[0])
                    next_str += rest[0]
                    rest = rest[1:]
                next_number = int(next_str)
                if 0 == len(rest):
                    print("Done, no more")
                    print("ending verse", next_number)
                    self._window.set_chapter(book_number, start_chapter_number)
                    self._window.UpdateTable(
                        list(
                            filter(
                                lambda x: (
                                    x.verse >= start_verse_number and x.verse <= next_number),
                                self._window.chapter.verses)),
                        self._window.book.bookName +
                        " " +
                        str(start_chapter_number) +
                        ":" +
                        str(start_verse_number) +
                        "-" +
                        str(next_number))
                    self._window.book.bookName

                    self._window.content_box.set_visible_child(
                        self._window.right_box)
                elif rest[0] == ':':
                    print("parsing verse")
                    end_verse_str = ''
                    rest = rest[1:]
                    while len(rest) > 0 and '0' <= rest[0] and '9' >= rest[0]:
                        # print(rest[0])
                        end_verse_str += rest[0]
                        rest = rest[1:]
                    end_verse_number = int(end_verse_str)
                    print("ending chapter", next_number)
                    print("ending verse", end_verse_number)
            elif rest[0] == ',':
                rest = rest[1:]
                lines = [start_verse_number] + rest.split(',')
                print(lines)
        elif rest[0] == '-':
            print("parsing end chapter")
            end_chapter_number = int(rest[1:])
            print("end_chapter_number", end_chapter_number)


def main(version):
    app = Application()
    return app.run(sys.argv)
