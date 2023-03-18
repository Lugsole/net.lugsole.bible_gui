import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from .config import user_data_dir
import shutil
import os
from gi.repository import Adw
from gi.repository import GObject, GLib, Gtk, Gio

from .Bible_Parser import BibleParser, allParsers
Adw.init()


@Gtk.Template(resource_path='/net/lugsole/bible_gui/settings.ui')
class BibleSettings(Adw.PreferencesWindow):
    __gtype_name__ = 'BibleSettings'
    translation = Gtk.Template.Child()
    importTranslation = Gtk.Template.Child()

    def __init__(self, App):
        super().__init__()
        self.App = App
        self.bible_file = ""
        self.translation_array = []
        try:
            settings = Gio.Settings.new(self.App.BASE_KEY)
            self.bible_file = settings.get_string("bible-translation")
        except Exception:
            print("gsettings error")
        self.importTranslation.connect('clicked', self.import_translation)
        self.translations_load()
        self.show()
        if not os.path.isdir(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)

    def copy_translation(self, filename):
        shutil.copy(filename, user_data_dir)
        self.translations_load()

    def import_translation(self, button):
        chooser = Gtk.FileChooserNative()
        chooser.set_transient_for(self)
        chooser.set_action(Gtk.FileChooserAction.OPEN)

        filter = Gtk.FileFilter()
        filter.set_name("Supported Bible files")
        chooser.add_filter(filter)
        for parser in allParsers:
            filter1 = Gtk.FileFilter()
            filter1.set_name(parser.getParserName(parser))
            for ending in parser.getParserEndings(parser):
                filter.add_pattern("*."+ ending)
                filter1.add_pattern("*."+ ending)
            chooser.add_filter(filter1)
        filter = Gtk.FileFilter()
        filter.set_name("All Files")
        filter.add_pattern("*")
        chooser.add_filter(filter)

        chooser.connect('response', self.import_translation_load)
        chooser.show()
        self.chooser = chooser

    def import_translation_load(self, chooser, res):
        if res == Gtk.ResponseType.ACCEPT:
            for file in chooser.get_files():
                self.copy_translation(file.get_path())
            chooser.destroy()
            self.chooser.destroy()
        else:
            chooser.destroy()
            self.chooser.destroy()

    def translations_load(self):
        for item in self.translation_array:
            self.translation.remove(item)
        self.translation_array = []
        all_files = []
        base = user_data_dir
        for root, dirs, files in os.walk(base):
            for filename in files:
                rel_path = os.path.join(root, filename)
                all_files.append(rel_path)
        all_files.sort()

        row = BibleTranslationRow("Default", self.translations_change, "", None)
        if self.bible_file == "":
            row.select()

        def_check = row.get_check()
        self.translation.add(row)
        self.translation_array.append(row)
        for bible_file in all_files:
            try:
                p = BibleParser(bible_file)
                if p is not None:
                    p.loadInfo()

                    row = BibleTranslationRow(
                        p.bible.translationName,
                        self.translations_change,
                        os.path.relpath(bible_file, base),
                        def_check)
                    if str(os.path.relpath(p.file_name,base)) == str(self.bible_file):
                        row.select()
                    else:
                        row.deselect()
                    self.translation.add(row)
                    self.translation_array.append(row)
            except Exception as error:
                print(bible_file, "Must not be a bible file")
                print(error)

    def translations_change(self, button, data):
        try:
            settings = Gio.Settings.new(self.App.BASE_KEY)
            settings.set_string("bible-translation", data)
            self.bible_file = settings.get_string("bible-translation")
        except Exception:
            print("gsettings error")


class BibleTranslationRow(Adw.ActionRow):
    def __init__(self, p, cb, rel_path, main_check):
        super().__init__()

        base = user_data_dir
        self.cb = cb
        self.rel_path = rel_path
        self.set_property("title", str(p))
        self.button = Gtk.CheckButton()
        self.button.add_css_class("selection-mode")
        self.button.connect('toggled', self.callback, rel_path)
        self.button.show()
        self.button.set_valign(Gtk.Align.CENTER)
        if main_check is not None:
            self.button.set_group(main_check)

        self.set_activatable_widget(self.button)
        self.box = Gtk.Box()
        self.box.append(self.button)
        self.add_suffix(self.box)
        self.show()

    def deselect(self):
        self.button.set_active(False)

    def select(self):
        self.button.set_active(True)

    def callback(self, button, data):
        if button.get_active():
            self.cb(self, self.rel_path)
    def get_check(self):
        return self.button
