import dbus
from common.path import ServicePath,PathType
from services.device_services.device_service import DeviceService,DeviceServiceType
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
        super().add_service_path(service_path,infos)
        new_service = self.service_paths[service_path]
        new_service.properties = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        new_service.listener = new_service.properties.connect_to_signal("PropertiesChanged",self.heart_rate_handler)
        new_service.infos['notifying'] = True
        new_service.interface.StartNotify()

    def heart_rate_handler(self,interface,dictionary,unused):
        if 'Value' in dictionary:
            value = int.from_bytes(bytearray(dictionary['Value']), "big")
            for callback in self.callbacks:
                callback(value)

