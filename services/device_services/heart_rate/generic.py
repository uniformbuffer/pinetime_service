import dbus
from common.path import ServicePath,PathType
from common.event_type import EventType
from services.device_services import DeviceService,DeviceServiceType
from services.device_services.heart_rate import HeartRateService

class GenericHeartRateService(HeartRateService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")
        service_type = uuid.split('-')[0]
        if service_type == "00002a37":
            return True
        else:
            return False

    def heart_rates(self):
        heart_rates = {}
        for service_path in self.service_paths:
            heart_rates[service_path] = int.from_bytes(bytearray(self.service_paths[service_path].interface.ReadValue({}),'big'))
        return heart_rates

    def add_service_path(self,service_path: str, infos: {}):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        properties = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        listener = properties.connect_to_signal("PropertiesChanged",self.heart_rate_handler)
        infos['notifying'] = True
        interface.StartNotify()
        self.service_paths[service_path] = ServicePath(properties,listener,interface,infos)

    def remove_service_path(self,service_path: str):
        if service_path in self.service_paths:
            del self.service_paths[service_path]

    def list_service_paths(self)->[str]:
        list(self.service_paths.keys())

    def heart_rate_handler(self,interface,dictionary,unused):
        if 'Value' in dictionary:
            value = int.from_bytes(bytearray(dictionary['Value']), "big")
            callbacks = self.get_callbacks(EventType.HEART_RATE)
            for index in callbacks:
                callbacks[index](value)

