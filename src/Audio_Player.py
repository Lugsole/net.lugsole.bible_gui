import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


class Player:
    cb = None
    def __init__(self, sound):
        # pathname2url escapes non-URL-safe characters
        import os
        from urllib.request import pathname2url

        Gst.init(None)

        self.playbin = Gst.ElementFactory.make('playbin', 'playbin3')
        if sound.startswith(('http://', 'https://')):
            self.playbin.props.uri = sound
        else:
            self.playbin.props.uri = 'file://' + pathname2url(os.path.abspath(sound))
        self.loop = GObject.MainLoop()
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call, self.loop)

    def bus_call(self, bus, message, loop):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.loop.quit()
            if self.cb is not None:
                self.cb()
        else:
            pass
        return True

    def add_callback(self,cb):
        self.cb = cb

    def Play(self):
        set_result = self.playbin.set_state(Gst.State.PLAYING)
        if set_result == Gst.StateChangeReturn.FAILURE:
            raise PlaysoundException(
                "playbin.set_state returned " + repr(set_result))

    def Pause(self):
        set_result = self.playbin.set_state(Gst.State.PAUSED)
        if set_result == Gst.StateChangeReturn.FAILURE:
            raise PlaysoundException(
                "playbin.set_state returned " + repr(set_result))

    def end(self):
        set_result = self.playbin.set_state(Gst.State.NULL)
        if set_result == Gst.StateChangeReturn.FAILURE:
            raise PlaysoundException(
                "playbin.set_state returned " + repr(set_result))

    def getstate(self):
        (ret, state, pending) = self.playbin.get_state(Gst.CLOCK_TIME_NONE)
        return state
