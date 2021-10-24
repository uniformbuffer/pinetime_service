import dbus
from common.call import Call
from common.event_type import EventType
from services.host_services import HostService,HostServiceType

class CallService(HostService):
    def call_handler(self,call_path,dictionary):
        inbound = bool(dictionary['org.gnome.Calls.Call']['Inbound'])
        if inbound:
            source = dictionary['org.gnome.Calls.Call']['DisplayName']
            number = dictionary['org.gnome.Calls.Call']['Id']

            accept_callback = lambda: dbus.Interface(self.session_bus.get_object('org.gnome.Calls', call_path), 'org.gnome.Calls.Call').Accept()
            hangup_callback = lambda: dbus.Interface(self.session_bus.get_object('org.gnome.Calls', call_path), 'org.gnome.Calls.Call').Hangup()
            call = Call(source,number,accept_callback,hangup_callback)
            self.current_call = call
            callbacks = self.get_callbacks(EventType.CALL)
            for index in callbacks:
                callbacks[index](call)

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
        return HostServiceType.CALL

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
