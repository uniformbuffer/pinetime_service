import dbus
from enum import Enum
from common.notification import Notification,NotificationType
from common.path import device_from_path,PathType,ServicePath
from common.call import Call,CallAnswer
from common.event_type import EventType
from services.device_services.call import CallService


class CallServiceType(Enum):
    UNKNOWN = 0
    REQUEST = 1
    EVENT = 2

    def from_uuid(uuid: str):
        service_type = uuid.split('-')[0]
        if uuid == "00020001-78fc-48fe-8e23-433b3a1942d0":
            return CallServiceType.EVENT
        elif service_type == "00002a46":
            return CallServiceType.REQUEST
        else:
            return CallServiceType.UNKNOWN

class InfinitimeCallService(CallService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)
        self.service_paths = {}
        self.request_service = None
        self.event_service = None

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'alias' in infos:
            alias = infos['alias']
        else:
            device_path = device_from_path(service_path)
            alias = dbus.Interface(system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.Device1", "Alias")
        if not alias.lower().startswith("infinitime"):
            return False

        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")

        if CallServiceType.from_uuid(uuid) != CallServiceType.UNKNOWN:
            return True
        else:
            return False

    def add_service_path(self,service_path: str, infos: {}):
        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")

        notification_service_type = CallServiceType.from_uuid(uuid)
        if notification_service_type == CallServiceType.REQUEST:
            interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            self.request_service = ServicePath(None,None,interface,{})
        elif notification_service_type == CallServiceType.EVENT:
            interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            interface.StartNotify()
            properties = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
            signal = properties.connect_to_signal("PropertiesChanged",self.call_answer_handler)
            self.event_service = ServicePath(properties,signal,interface,{})

    def remove_service_path(self,service_path: str):
        if service_path in self.service_paths:
            del self.service_paths[service_path]

    def list_service_paths(self)->[str]:
        service_paths = []
        if self.request_service != None:
            service_paths.append(self.request_service.interface.object_path)
        if self.event_service != None:
            service_paths.append(self.event_service.interface.object_path)
        return service_paths

    def notify_call(self, call: Call):
        # InfiniTime convert the first 3 bytes (8 bits) into an unsigned int that specify what kind of message it has received
        # Currently the available types are all the same except for CALL
        if self.request_service.interface != None:
            call_value = 3
            notification = call.source+'\n'+call.number
            message = call_value.to_bytes(3,byteorder='little') + str(notification).encode('utf_8')
            self.request_service.interface.WriteValue(message,{})

    def call_answer_handler(self,interface,message,unused):
        if 'Value' in message:
            call_event = CallAnswer(int.from_bytes(bytearray(message['Value']), "big"))
            callbacks = self.get_callbacks(EventType.CALL_ANSWER)
            for index in callbacks:
                callbacks[index](call_event)

