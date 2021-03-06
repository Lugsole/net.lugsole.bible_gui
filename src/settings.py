

import gi

from .Bible_Parser import BibleParser, allParsers
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, GLib, Gtk, Gio
gi.require_version('Handy', '1')
from gi.repository import Handy
import os
import shutil
Handy.init()


@Gtk.Template(resource_path='/net/lugsole/bible_gui/settings.ui')
class BibleSettings(Handy.PreferencesWindow):
    __gtype_name__ = 'BibleSettings'
    translation = Gtk.Template.Child()
    importTranslation = Gtk.Template.Child()
    def __init__(self, App, BASE_KEY):
        super().__init__()
        self.BASE_KEY = BASE_KEY
        self.App = App
        self.bible_file = ""
        self.current_translation_row = None

        try:
            settings = Gio.Settings.new(self.BASE_KEY)
            self.bible_file = settings.get_string("bible-translation")
        except Exception:
            print("gsettings error")
        self.importTranslation.connect('clicked', self.import_translation)
        self.translations_load()
        self.show()

    def copy_translation(self,filename):
        shutil.copy(filename, GLib.get_user_data_dir())
        self.translations_load()

    def import_translation(self, button):
        chooser = Gtk.FileChooserNative(title="Import Bible Translation")
        filter = Gtk.FileFilter()
        filter.set_name("Any Bible format")
        for parser in allParsers:
            for ending in parser.getParserEndings(parser):
                filter.add_pattern("*."+ ending)
        chooser.add_filter(filter)
        for parser in allParsers:
            filter = Gtk.FileFilter()
            filter.set_name(parser.getParserName(parser))
            for ending in parser.getParserEndings(parser):
                filter.add_pattern("*."+ ending)
            chooser.add_filter(filter)
        filter = Gtk.FileFilter()
        filter.set_name("Any File")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        self.get_focus()
        res = chooser.run()
        if res == Gtk.ResponseType.ACCEPT:
            filename = chooser.get_filename()
            chooser.destroy()
            self.copy_translation(filename)
        else:
            chooser.destroy()

    def translations_load(self):
        for item in self.translation.get_children():
            if isinstance(item, BibleTranslationRow):
                self.translation.remove(item)
        all_files = []
        base = GLib.get_user_data_dir()
        for root, dirs, files in os.walk(base):
            for filename in files:
                rel_path = os.path.join(root, filename)
                all_files.append(rel_path)
        all_files.sort()
        for bible_file in all_files:
            p = BibleParser(bible_file)
            if p is not None:
                p.loadInfo()
                row = BibleTranslationRow(p,
                                          self.translations_change,
                                          os.path.relpath(bible_file, base))
                if str(os.path.relpath(p.file_name,base)) == str(self.bible_file):
                    row.select()
                    self.current_translation_row = row
                self.translation.add(row)

    def translations_change(self, button, data):
        try:
            settings = Gio.Settings.new(self.BASE_KEY)
            settings.set_string("bible-translation", data)
            self.bible_file = settings.get_string("bible-translation")
            if self.current_translation_row is not None:
                self.current_translation_row.deselect()
            button.select()
            self.current_translation_row = button
        except Exception:
            print("gsettings error")

class BibleTranslationRow(Handy.ActionRow):
    def __init__(self, p, cb, rel_path):
        super().__init__()

        base = GLib.get_user_data_dir()
        self.cb = cb
        self.rel_path = rel_path
        self.set_property("title", str(p.bible.translationName))
        self.button = Gtk.Button(label="Change")
        self.button.connect('clicked', self.callback, rel_path)
        self.button.show()

        self.checkmark= Gtk.Image.new_from_icon_name("emblem-ok-symbolic",
                                                     Gtk.IconSize.MENU)

        self.set_activatable_widget(self.button)
        self.add(self.button)
        self.add(self.checkmark)
        self.show()
    def deselect(self):
        self.button.show()
        self.checkmark.hide()
    def select(self):
        self.button.hide()
        self.checkmark.show()
    def callback(self, button, data):
        self.cb(self, self.rel_path)
        
