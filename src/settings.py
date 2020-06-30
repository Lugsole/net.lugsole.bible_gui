

import gi

from .Bible_Parser import BibleParser
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, GLib, Gtk, Gio
gi.require_version('Handy', '0.0')
from gi.repository import Handy
import os
Handy.init()


class Settings:
    __gtype_name__ = 'BibleWindow'

    def __init__(self, App, BASE_KEY):
        self.BASE_KEY = BASE_KEY
        self.App = App
        builder = Gtk.Builder()
        builder.add_from_resource('/net/lugsole/bible_gui/settings.ui')
        self.teanslations = builder.get_object("translation")
        window = builder.get_object("window")
        self.translations_load()
        window.show()
        try:
            settings = Gio.Settings.new(self.BASE_KEY)
            print(settings)
            print(settings.get_string("bible-translation"))
        except Exception:
            print("gsettings error")

    def translations_load(self):
        base = GLib.get_user_data_dir()
        count = 0
        root_box = Gtk.VBox()
        root_box.show()
        for root, dirs, files in os.walk(base):
            for filename in files:
                print(os.path.join(root, filename))
                rel_path = os.path.relpath(os.path.join(root, filename), base)
                p = BibleParser(os.path.join(root, filename))
                if p is not None:
                    p.loadInfo()
                    count += 1
                    box = Gtk.HBox()
                    box.show()
                    name = Gtk.Label(str(p.bible.translationName))
                    name.show()
                    name.set_ellipsize(3)

                    name.set_xalign(0)
                    name.set_yalign(0)
                    box.pack_start(name, True, True, 0)
                    button = Gtk.Button(name, label="Change")
                    button.connect('clicked', self.translations_change, rel_path)
                    button.show()
                    box.pack_start(button, False, True, 0)
                    root_box.pack_start(box, True, True, 0)
                    # print(str(p.bible.translationName))
                    # print("language",str(p.bible.language))
                    # print(str(p.bible.translationInformation))
        self.teanslations.add(root_box)

    def translations_change(self, button, path):
        try:
            settings = Gio.Settings.new(self.BASE_KEY)
            print(settings)
            print(settings.set_string("bible-translation", path))
            print(path)
        except Exception:
            print("gsettings error")

