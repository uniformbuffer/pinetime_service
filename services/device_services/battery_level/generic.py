import dbus
from common.path import ServicePath,PathType
from services.device_services.battery_level import BatteryLevelService
from services.device_services import DeviceService

class GenericBatteryLevelService(BatteryLevelService):
    def battery_level_handler(self,interface,dictionary,unused):
        if 'Value' in dictionary:
            value = int.from_bytes(bytearray(dictionary['Value']), "big")
            for callback in self.callbacks:
                callback(value)

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")
        service_type = uuid.split('-')[0]
        if service_type == "00002a19":
            return True
        else:
            return False

    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    def battery_levels(self):
        battery_levels = {}
        for service_path in self.service_paths:
            battery_levels[service_path] = int(self.service_paths[service_path].properties.Get("org.bluez.Battery1", "Percentage"))
        return battery_levels

    def add_service_path(self,service_path: str, infos: {}):
        super().add_service_path(service_path,infos)
        new_service = self.service_paths[service_path]
        new_service.properties = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        new_service.listener = new_service.properties.connect_to_signal("PropertiesChanged",self.battery_level_handler)
        new_service.infos['notifying'] = True
        new_service.interface.StartNotify()

    def remove_service_path(self,path: str):
        path = str(path)
        if path in self.service_paths:
            del self.service_paths[path]

    def add_callback(self,callback):
        self.callbacks.append(callback)

    def remove_callback(self,callback):
        self.callbacks.remove(callback)
