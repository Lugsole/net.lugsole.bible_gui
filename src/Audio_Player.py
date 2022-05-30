import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, Gio, GLib, Gtk



import re

class DBusInterface:

    def __init__(self, name, path, application):
        """Etablish a D-Bus session connection

        :param str name: interface name
        :param str path: object path
        :param GtkApplication application: The Application object
        """
        self._path = path
        self._signals = None
        Gio.bus_get(Gio.BusType.SESSION, None, self._bus_get_sync, name)

    def _bus_get_sync(self, source, res, name):
        try:
            self._con = Gio.bus_get_finish(res)
        except GLib.Error as e:
            print(
                "Unable to connect to to session bus: {}".format(e.message))
            return

        Gio.bus_own_name_on_connection(
            self._con, name, Gio.BusNameOwnerFlags.NONE, None, None)

        method_outargs = {}
        method_inargs = {}
        signals = {}
        for interface in Gio.DBusNodeInfo.new_for_xml(self.__doc__).interfaces:

            for method in interface.methods:
                method_outargs[method.name] = "(" + "".join(
                    [arg.signature for arg in method.out_args]) + ")"
                method_inargs[method.name] = tuple(
                    arg.signature for arg in method.in_args)

            for signal in interface.signals:
                args = {arg.name: arg.signature for arg in signal.args}
                signals[signal.name] = {
                    'interface': interface.name, 'args': args}

            self._con.register_object(
                object_path=self._path, interface_info=interface,
                method_call_closure=self._on_method_call)

        self._method_inargs = method_inargs
        self._method_outargs = method_outargs
        self._signals = signals

    def _on_method_call(
        self, connection, sender, object_path, interface_name, method_name,
            parameters, invocation):
        """GObject.Closure to handle incoming method calls.

        :param Gio.DBusConnection connection: D-Bus connection
        :param str sender: bus name that invoked the method
        :param srt object_path: object path the method was invoked on
        :param str interface_name: name of the D-Bus interface
        :param str method_name: name of the method that was invoked
        :param GLib.Variant parameters: parameters of the method invocation
        :param Gio.DBusMethodInvocation invocation: invocation
        """
        args = list(parameters.unpack())
        for i, sig in enumerate(self._method_inargs[method_name]):
            if sig == 'h':
                msg = invocation.get_message()
                fd_list = msg.get_unix_fd_list()
                args[i] = fd_list.get(args[i])

        method_snake_name = DBusInterface.camelcase_to_snake_case(method_name)
        try:
            result = getattr(self, method_snake_name)(*args)
        except ValueError as e:
            print(method_snake_name)
            invocation.return_dbus_error(interface_name, str(e))
            return
        result = (result,)

        out_args = self._method_outargs[method_name]
        if out_args != '()':
            variant = GLib.Variant(out_args, result)
            invocation.return_value(variant)
        else:
            invocation.return_value(None)

    def _dbus_emit_signal(self, signal_name, values):
        if self._signals is None:
            return
        signal = self._signals[signal_name]
        parameters = []
        for arg_name, arg_signature in signal['args'].items():
            value = values[arg_name]
            parameters.append(GLib.Variant(arg_signature, value))

        variant = GLib.Variant.new_tuple(*parameters)
        self._con.emit_signal(
            None, self._path, signal['interface'], signal_name, variant)

    @staticmethod
    def camelcase_to_snake_case(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return '_' + re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Player(DBusInterface):
    '''
    <!DOCTYPE node PUBLIC '-//freedesktop//DTD D-BUS Object Introspection 1.0//EN'
    'http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd'>
    <node>
        <interface name='org.freedesktop.DBus.Introspectable'>
            <method name='Introspect'>
                <arg name='data' direction='out' type='s'/>
            </method>
        </interface>
        <interface name="org.freedesktop.DBus.Properties">
            <method name="Get">
                <arg type="s" name="interface_name" direction="in"/>
                <arg type="s" name="property_name" direction="in"/>
                <arg type="v" name="value" direction="out"/>
            </method>
            <method name="GetAll">
                <arg type="s" name="interface_name" direction="in"/>
                <arg type="a{sv}" name="properties" direction="out"/>
                <annotation name="org.qtproject.QtDBus.QtTypeName.Out0" value="QVariantMap" />
            </method>
            <method name="Set">
                <arg type="s" name="interface_name" direction="in"/>
                <arg type="s" name="property_name" direction="in"/>
                <arg type="v" name="value" direction="in"/>
            </method>
            <signal name="PropertiesChanged">
                <arg type="s" name="interface_name"/>
                <arg type="a{sv}" name="changed_properties"/>
                <arg type="as" name="invalidated_properties"/>
                <annotation name="org.qtproject.QtDBus.QtTypeName.Out1" value="QVariantMap" />
            </signal>
        </interface>
        <interface name='org.mpris.MediaPlayer2'>
            <method name='Raise'>
            </method>
            <method name='Quit'>
            </method>
            <property name='CanQuit' type='b' access='read' />
            <property name='Fullscreen' type='b' access='readwrite' />
            <property name='CanRaise' type='b' access='read' />
            <property name='HasTrackList' type='b' access='read'/>
            <property name='Identity' type='s' access='read'/>
            <property name='DesktopEntry' type='s' access='read'/>
            <property name='SupportedUriSchemes' type='as' access='read'/>
            <property name='SupportedMimeTypes' type='as' access='read'/>
        </interface>
        <interface name='org.mpris.MediaPlayer2.Player'>
            <method name='Next'/>
            <method name='Previous'/>
            <method name='Pause'/>
            <method name='PlayPause'/>
            <method name='Stop'/>
            <method name='Play'/>
            <method name='Seek'>
                <arg direction='in' name='Offset' type='x'/>
            </method>
            <method name='SetPosition'>
                <arg direction='in' name='TrackId' type='o'/>
                <arg direction='in' name='Position' type='x'/>
            </method>
            <method name='OpenUri'>
                <arg direction='in' name='Uri' type='s'/>
            </method>
            <signal name='Seeked'>
                <arg name='Position' type='x'/>
            </signal>
            <property name='PlaybackStatus' type='s' access='read'/>
            <property name='LoopStatus' type='s' access='readwrite'/>
            <property name='Rate' type='d' access='readwrite'/>
            <property name='Shuffle' type='b' access='readwrite'/>
            <property name='Metadata' type='a{sv}' access='read'/>
            <property name='Volume' type='d' access='readwrite'/>
            <property name='Position' type='x' access='read'/>
            <property name='MinimumRate' type='d' access='read'/>
            <property name='MaximumRate' type='d' access='read'/>
            <property name='CanGoNext' type='b' access='read'/>
            <property name='CanGoPrevious' type='b' access='read'/>
            <property name='CanPlay' type='b' access='read'/>
            <property name='CanPause' type='b' access='read'/>
            <property name='CanSeek' type='b' access='read'/>
            <property name='CanControl' type='b' access='read'/>
        </interface>
    </node>
    '''
    MEDIA_PLAYER2_IFACE = 'org.mpris.MediaPlayer2'
    MEDIA_PLAYER2_PLAYER_IFACE = 'org.mpris.MediaPlayer2.Player'
    MEDIA_PLAYER2_TRACKLIST_IFACE = 'org.mpris.MediaPlayer2.TrackList'
    MEDIA_PLAYER2_PLAYLISTS_IFACE = 'org.mpris.MediaPlayer2.Playlists'

    _playlist_nb_songs = 10

    def __init__(self, app):
        name = "org.mpris.MediaPlayer2.{}".format("Bible")
        path = '/org/mpris/MediaPlayer2'
        self.file = ""
        super().__init__(name, path, app)

        self._app = app

        self._title = "Title"
        self._album =  "Album"
        self._artist = ["Artist"]
        self._album_artist = ["Artist"]
        self.playbin = None

    def _properties_changed(self, interface_name, changed_properties,
                          invalidated_properties):
        self.__bus.emit_signal(None,
                               self.__MPRIS_PATH,
                               "org.freedesktop.DBus.Properties",
                               "PropertiesChanged",
                               GLib.Variant.new_tuple(
                                   GLib.Variant("s", interface_name),
                                   GLib.Variant("a{sv}", changed_properties),
                                   GLib.Variant("as", invalidated_properties)))

    def _get_metadata(self, coresong=None, index=None):
        # print(self._artist)
        metadata = {
            'xesam:url': GLib.Variant('s', self.file),
            'mpris:length': GLib.Variant('x', 0),
            'xesam:title': GLib.Variant('s', self._title),
            'xesam:album': GLib.Variant('s', self._album),
            'xesam:artist': GLib.Variant('as', self._artist),
            'xesam:albumArtist': GLib.Variant('as', self._album_artist)
        }
        if self.playbin is not None:
            #print(self.playbin.query_duration(Gst.Format.TIME))
            rc, duration = self.playbin.query_duration(Gst.Format.TIME)
            if rc:
                metadata['mpris:length'] = GLib.Variant('i', duration/1000)
        return metadata


    def _get(self, interface_name, property_name):
        try:
            return self._get_all(interface_name)[property_name]
        except KeyError:
            msg = "MPRIS does not handle {} property from {} interface".format(
                property_name, interface_name)
            self._log.warning(msg)
            raise ValueError(msg)

    def _get_all(self, interface_name):
        if interface_name == Player.MEDIA_PLAYER2_IFACE:
            application_id = self._app.props.application_id
            return {
                'CanQuit': GLib.Variant('b', True),
                'Fullscreen': GLib.Variant('b', False),
                'CanSetFullscreen': GLib.Variant('b', False),
                'CanRaise': GLib.Variant('b', True),
                'HasTrackList': GLib.Variant('b', False),
                'Identity': GLib.Variant('s', 'Bible'),
                'DesktopEntry': GLib.Variant('s', application_id),
                'SupportedUriSchemes': GLib.Variant('as', [
                    'file'
                ]),
                'SupportedMimeTypes': GLib.Variant('as', [
                    'application/ogg',
                    'audio/x-vorbis+ogg',
                    'audio/x-flac',
                    'audio/mpeg'
                ]),
            }
        elif interface_name == Player.MEDIA_PLAYER2_PLAYER_IFACE:
            position_msecond = 0
            playback_status = "Playing"
            is_shuffle = False
            can_play = True
            has_previous = False
            return {
                'PlaybackStatus': GLib.Variant('s', self.get_status()),
                'LoopStatus': GLib.Variant('s', "None"),
                'Rate': GLib.Variant('d', 1.0),
                'Shuffle': GLib.Variant('b', is_shuffle),
                'Metadata': GLib.Variant('a{sv}', self._get_metadata()),
                'Position': GLib.Variant('x', position_msecond),
                'MinimumRate': GLib.Variant('d', 1.0),
                'MaximumRate': GLib.Variant('d', 1.0),
                'CanGoNext': GLib.Variant('b', True),
                'CanGoPrevious': GLib.Variant('b', True),
                'CanPlay': GLib.Variant('b', self.has_content()),
                'CanPause': GLib.Variant('b', self.has_content()),
                'CanSeek': GLib.Variant('b', True),
                'CanControl': GLib.Variant('b', True),
            }
        elif interface_name == 'org.freedesktop.DBus.Properties':
            return {}
        elif interface_name == 'org.freedesktop.DBus.Introspectable':
            return {}
        else:
            self._log.warning(
                "MPRIS does not implement {} interface".format(interface_name))

    def _set(self, interface_name, property_name, new_value):
        if interface_name == MPRIS.MEDIA_PLAYER2_IFACE:
            if property_name == 'Fullscreen':
                pass
        elif interface_name == MPRIS.MEDIA_PLAYER2_PLAYER_IFACE:
            if property_name in ['Rate', 'Volume', 'LoopStatus', 'Shuffle']:
                pass
        else:
            self._log.warning(
                "MPRIS does not implement {} interface".format(interface_name))

    def _properties_changed(self, interface_name, changed_properties,
                            invalidated_properties):
        parameters = {
            'interface_name': interface_name,
            'changed_properties': changed_properties,
            'invalidated_properties': invalidated_properties
        }
        self._dbus_emit_signal('PropertiesChanged', parameters)


    def _introspect(self):
        return self.__doc__

    def get_status(self):
        if self.playbin is None:
            return "Stopped"
        (ret, state, pending) = self.playbin.get_state(Gst.CLOCK_TIME_NONE)
        if state == Gst.State.PLAYING:
            return "Playing"
        elif state == Gst.State.PAUSED:
            return "Paused"
        else:
            return "Stopped"

    def has_content(self):
        return self.playbin is not None

    def _next(self):
        if self._app._window:
            self._app._window.next()

    def _previous(self):
        if self._app._window:
            self._app._window.previous()



    cb = None
    def start_file(self, sound):
        # pathname2url escapes non-URL-safe characters
        import os
        from urllib.request import pathname2url

        Gst.init(None)
        if self.playbin is not None:
            self.end()
        self.playbin = Gst.ElementFactory.make('playbin', 'playbin3')
        if sound.startswith(('http://', 'https://')):
            self.playbin.props.uri = sound
        else:
            self.playbin.props.uri = 'file://' + pathname2url(os.path.abspath(sound))
        self.file = sound
        self.loop = GObject.MainLoop()
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call, self.loop)
        properties = {
                'CanPlay': GLib.Variant('b', self.has_content()),
                'CanPause': GLib.Variant('b', self.has_content())}
        self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])

    def bus_call(self, bus, message, loop):
        t = message.type
        if t == Gst.MessageType.EOS:
            # print(t)
            self.loop.quit()
            if self.cb is not None:
                self.cb()
        elif t == Gst.MessageType.STATE_CHANGED:
            # print(message)
            old_state, new_state, pending_state = message.parse_state_changed()
            if self.state_change_cb is not None:
                self.state_change_cb()
            # print(old_state, new_state, pending_state)
            if old_state == Gst.State.NULL:
                properties = {"Metadata": GLib.Variant("a{sv}", self._get_metadata())}
                self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])
            pass
        else:
            #print("Some other message type: " + str(message.type))
            pass
        return True

    def set_title(self, title):
        self._title = title
        properties = {"Metadata": GLib.Variant("a{sv}", self._get_metadata())}
        self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])

    def set_artist(self, artist):
        self._artist = artist
        self._album_artist = artist
        properties = {"Metadata": GLib.Variant("a{sv}", self._get_metadata())}
        self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])

    def set_album(self, album):
        self._album = album
        properties = {"Metadata": GLib.Variant("a{sv}", self._get_metadata())}
        self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])

    def add_callback(self,cb):
        self.cb = cb

    def add_state_change_callback(self,cb):
        self.state_change_cb = cb

    def _play(self):
        set_result = self.playbin.set_state(Gst.State.PLAYING)
        if set_result == Gst.StateChangeReturn.FAILURE:
            raise PlaysoundException(
                "playbin.set_state returned " + repr(set_result))
        properties = {"PlaybackStatus": GLib.Variant("s", self.get_status())}
        self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])

    def _pause(self):
        set_result = self.playbin.set_state(Gst.State.PAUSED)
        if set_result == Gst.StateChangeReturn.FAILURE:
            raise PlaysoundException(
                "playbin.set_state returned " + repr(set_result))
        properties = {"PlaybackStatus": GLib.Variant("s", self.get_status())}
        self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])


    def _play_pause(self):
        (ret, state, pending) = self.playbin.get_state(Gst.CLOCK_TIME_NONE)
        if state == Gst.State.PLAYING:
            self._pause()
        else:
            self._play()

    def _seek(self,time):
        print("_seek",time)
        success, position = self.playbin.query_position(Gst.Format.TIME)
        if not success:
                raise GenericException("Couldn't fetch current song position to update slider")
        print(position, time*1000)
        print(position + time*1000)
        if position + time*1000 > 0:
            self.playbin.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, position + time*1000)
        else:
            self.playbin.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)

    def _raise(self):
        self._app.raide_main_window()

    def end(self):
        if self.playbin is None:
            return
        set_result = self.playbin.set_state(Gst.State.NULL)
        if set_result == Gst.StateChangeReturn.FAILURE:
            raise PlaysoundException(
                "playbin.set_state returned " + repr(set_result))
        else:
            self.playbin = None
        properties = {
                'CanPlay': GLib.Variant('b', self.has_content()),
                'CanPause': GLib.Variant('b', self.has_content())}
        self._properties_changed(self.MEDIA_PLAYER2_PLAYER_IFACE, properties, [])

    def getstate(self):
        if self.playbin is not None:
            (ret, state, pending) = self.playbin.get_state(Gst.CLOCK_TIME_NONE)
            return state
        else:
            return Gst.State.NULL
