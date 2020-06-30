import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


class Player:
    def __init__(self, sound):
        # pathname2url escapes non-URL-safe characters
        import os
        try:
            from urllib.request import pathname2url
        except ImportError:
            # python 2
            from urllib import pathname2url

        Gst.init(None)

        self.playbin = Gst.ElementFactory.make('playbin', 'playbin3')
        if sound.startswith(('http://', 'https://')):
            self.playbin.props.uri = sound
        else:
            self.playbin.props.uri = 'file://' + pathname2url(os.path.abspath(sound))
        self.loop = GObject.MainLoop()
        print(pathname2url(os.path.abspath(sound)))
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call, self.loop)
        print(dir(Gst.MessageType))

    def bus_call(self, bus, message, loop):
        t = message.type
        if t == Gst.MessageType.EOS:
            print("End-of-stream\n")
            self.loop.quit()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error: %s: %s\n" % (err, debug))
            self.loop.quit()

        elif t == Gst.MessageType.STATE_CHANGED:
            '''
            (ret, state1, state2) = self.playbin.get_state(Gst.CLOCK_TIME_NONE)
            state = state1
            state_str = ""
            if state == Gst.State.VOID_PENDING:
                state_str = "VOID_PENDING"
            elif state == Gst.State.NULL:
                state_str = "NULL"
            elif state == Gst.State.READY:
                state_str = "READY"
            elif state == Gst.State.PAUSED:
                state_str = "PAUSED"
            elif state == Gst.State.PLAYING:
                state_str = "PLAYING"
            else:
                state_str = "unknown"
            print("State change", state_str)
            state = state2
            state_str = ""
            if state == Gst.State.VOID_PENDING:
                state_str = "VOID_PENDING"
            elif state == Gst.State.NULL:
                state_str = "NULL"
            elif state == Gst.State.READY:
                state_str = "READY"
            elif state == Gst.State.PAUSED:
                state_str = "PAUSED"
            elif state == Gst.State.PLAYING:
                state_str = "PLAYING"
            else:
                state_str = "unknown"
                '''
            print("State change")
        return True

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
