import dbus
from services.device_services.device_service import DeviceService,DeviceServiceType
from common.path import ServicePath

class BatteryLevelService(DeviceService):
    def battery_level_handler(self,interface,dictionary,unused):
        if 'Value' in dictionary:
            value = int.from_bytes(bytearray(dictionary['Value']), "big")
            for callback in self.callbacks:
                callback(value)
    
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path: str,service_paths: [str]):
        super().__init__()
        self.system_bus = system_bus
        self.device_path = device_path
        for service_path in service_paths:
            self.add_service_path(service_path)
        print("Initialized device service {} on {}".format(BatteryLevelService.service_type().name,device_path))

    def battery_levels(self):
        battery_levels = {}
        for service_path in self.service_paths:
            battery_levels[service_path] = int(self.service_paths[service_path].properties.Get("org.bluez.Battery1", "Percentage"))
        return battery_levels
    
    def service_type():
        return DeviceServiceType.BATTERY_LEVEL
    
    def add_service_path(self,service_path: str):
        properties = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        listener = properties.connect_to_signal("PropertiesChanged",self.battery_level_handler)
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        members = {
            'notifying': False
        }
        interface.StartNotify()
        self.service_paths[service_path] = ServicePath(properties,listener,interface,members)

    def remove_service_path(self,path: str):
        path = str(path)
        if path in self.service_paths:
            del self.service_paths[path]

    def add_callback(self,callback):
        self.callbacks.append(callback)
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)
    
    def deinit(self):
        pass
