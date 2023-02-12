
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gettext import gettext as _
from .settings import BibleSettings
from .config import application_id, VERSION
from .Audio_Player import Player
from .window import BibleWindow
from gi.repository import Adw, Gtk, Gio, GLib
import sys


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=application_id,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.props.resource_base_path = "/net/lugsole/bible_gui"

        self.BASE_KEY = application_id
        GLib.set_application_name(_("Bible"))
        GLib.set_prgname(application_id)
        GLib.setenv("PULSE_PROP_media.role", "music", True)
        self.player = Player(self)
        self.create_action("preferences", self.launch_settings, ['<primary>comma'])
        action_print = Gio.SimpleAction.new("about", None)
        action_print.connect("activate", self.show_about)
        self.add_action(action_print)

    def do_activate(self):
        self.window = self.props.active_window
        if not self.window:
            self.window = BibleWindow(self, application=self)
        self.window.present()

        if self.props.application_id == "net.lugsole.bible_gui.Devel":
            self.window.get_style_context().add_class('devel')

    def raide_main_window(self):
        self.window.present()

    def launch_settings(self, e1, e2):
        settings = BibleSettings(self)
        if self.props.application_id == "net.lugsole.bible_gui.Devel":
            settings.get_style_context().add_class('devel')

    def show_about(self, e1, e2):
        dialog = Adw.AboutWindow()
        if self.props.application_id == "net.lugsole.bible_gui.Devel":
            dialog.get_style_context().add_class('devel')
        dialog.set_application_name(_("Bible"))
        dialog.set_comments(_("A Linux Bible app"))
        dialog.set_copyright("© 2020-2022 Lugsole")
        dialog.set_version(VERSION)
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_developers(["Lugsole"])
        dialog.set_application_icon(application_id)
        dialog.show()

    def create_action(self, name, callback, shortcuts=None, param=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
            param: an optional list of parameters for the action
        """
        action = Gio.SimpleAction.new(name, param)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

def main(version):

    app = Application()
    return app.run(sys.argv)
