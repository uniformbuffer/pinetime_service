import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from manager import BTManager

DBusGMainLoop(set_as_default=True)

manager = BTManager()

GLib.MainLoop().run()
