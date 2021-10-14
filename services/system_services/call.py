import dbus
from services.system_services.system_service import SystemService,SystemServiceType

class Call():
    def __init__(self,source,number):
        self.source = source
        self.number = number
    def __str__():
        return "Incoming call\n{}\n{}".format(self.source,self.number)

class CallService(SystemService):
    def call_handler(self,call_path,dictionary):
        inbound = bool(dictionary['org.gnome.Calls.Call']['Inbound'])
        if inbound:
            source = dictionary['org.gnome.Calls.Call']['DisplayName']
            number = dictionary['org.gnome.Calls.Call']['Id']
            call = Call(source,number)
            for callback in self.callbacks:
                callback(call)
            
            #dictionary['org.gnome.Calls.Call']['State']
            #dictionary['org.gnome.Calls.Call']['Protocol']
            #dictionary['org.gnome.Calls.Call']['Encrypted']
    
    def __init__(self,session_bus: dbus.SessionBus):
        super().__init__()
        self.call_listeners = [
            session_bus.add_signal_receiver(self.call_handler,path='/org/gnome/Calls',dbus_interface="org.freedesktop.DBus.ObjectManager",signal_name="InterfacesAdded")
        ]
    
    def service_type():
        return SystemServiceType.CALL
    
    def add_callback(self,callback):
        self.callbacks.append(callback)
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)
    
    def __exit__(self, exc_type, exc_value, traceback):
        for listener in self.call_listener:
            listener.remove()
