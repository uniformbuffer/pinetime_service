import dbus
from services.system_services.system_service import SystemService,SystemServiceType

class MPRISService(SystemService):
    def mpris_handler(self,name,old_owner,new_owner):
        if name.startswith('org.mpris.MediaPlayer2'):
            if old_owner == '' and new_owner != '':
                for callback in self.callbacks:
                    callback(True,new_owner)
                print(name+" opened!")
                 
            if new_owner == '' and old_owner != '':
                for callback in self.old_owner:
                    callback(False,new_owner)
                print(name+" closed!")
    
    def __init__(self,session_bus: dbus.SessionBus):
        super().__init__()
        self.session_bus = session_bus
        self.mpris_listener = self.session_bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').connect_to_signal("NameOwnerChanged",self.mpris_handler)

    def service_type():
        return SystemServiceType.MPRIS
    
    def add_callback(self,callback):
        self.callbacks.append(callback)
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)

    def deinit(self):
        self.mpris_listener.remove()
