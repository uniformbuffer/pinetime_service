import dbus
from gi.repository import GObject as gobject
from dbus.mainloop.glib import DBusGMainLoop
from manager import BTManager
DBusGMainLoop(set_as_default=True)

manager = BTManager()

gobject.MainLoop().run()
