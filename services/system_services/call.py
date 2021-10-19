import dbus
from services.system_services.system_service import SystemService,SystemServiceType

class Call():
    def __init__(self,source,number,accept_callback,hangup_callback):
        self.source = source
        self.number = number
        self.accept_callback = accept_callback
        self.hangup_callback = hangup_callback

    def accept(self):
        self.accept_callback()
    def hangup(self):
        self.hangup_callback()
    def __str__():
        return "Incoming call\n{}\n{}".format(self.source,self.number)

class CallService(SystemService):
    def call_handler(self,call_path,dictionary):
        inbound = bool(dictionary['org.gnome.Calls.Call']['Inbound'])
        if inbound:
            source = dictionary['org.gnome.Calls.Call']['DisplayName']
            number = dictionary['org.gnome.Calls.Call']['Id']

            accept_callback = lambda: dbus.Interface(self.session_bus.get_object('org.gnome.Calls', call_path), 'org.gnome.Calls.Call').Accept()
            hangup_callback = lambda: dbus.Interface(self.session_bus.get_object('org.gnome.Calls', call_path), 'org.gnome.Calls.Call').Hangup()
            call = Call(source,number,accept_callback,hangup_callback)
            self.current_call = call
            for callback in self.callbacks:
                callback(call)
            
            #dictionary['org.gnome.Calls.Call']['State']
            #dictionary['org.gnome.Calls.Call']['Protocol']
            #dictionary['org.gnome.Calls.Call']['Encrypted']
    
    def __init__(self,session_bus: dbus.SessionBus):
        super().__init__()
        self.session_bus = session_bus
        self.current_call = None
        self.call_listeners = [
            session_bus.add_signal_receiver(self.call_handler,path='/org/gnome/Calls',dbus_interface="org.freedesktop.DBus.ObjectManager",signal_name="InterfacesAdded")
        ]
    
    def service_type():
        return SystemServiceType.CALL
    
    def add_callback(self,callback):
        self.callbacks.append(callback)
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)
    
    def accept(self):
        if self.current_call != None:
            self.current_call.accept_callback()
            self.current_call = None

    def hangup(self):
        if self.current_call != None:
            self.current_call.hangup_callback()
            self.current_call = None

    def deinit(self):
        for listener in self.call_listener:
            listener.remove()
