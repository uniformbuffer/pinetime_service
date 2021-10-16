import dbus
from services.device_services.device_service import DeviceService,DeviceServiceType
from common.path import ServicePath

class HeartRateService(DeviceService):
    def heart_rate_handler(self,interface,dictionary,unused):
        if 'Value' in dictionary:
            value = int.from_bytes(bytearray(dictionary['Value']), "big")
            for callback in self.callbacks:
                callback(value)
    
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path: str,service_paths: [str]):
        super().__init__()
        self.system_bus = system_bus
        for service_path in service_paths:
            self.add_service_path(service_path)
        print("Initialized device service {} on {}".format(HeartRateService.service_type().name,device_path))
    
    def service_type():
        return DeviceServiceType.HEART_RATE
    
    def add_service_path(self,service_path: str):
        properties = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        listener = properties.connect_to_signal("PropertiesChanged",self.heart_rate_handler)
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        members = {
            'notifying': True
        }
        interface.StartNotify()
        self.service_paths[service_path] = ServicePath(properties,listener,interface,members)

    def remove_service_path(self,path: str):
        if path in self.service_paths:
            del self.service_paths[path]

    def add_callback(self,callback):
        self.callbacks.append(callback)
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)

    def heart_rates(self):
        heart_rates = {}
        for service_path in self.service_paths:
            heart_rates[service_path] = int.from_bytes(bytearray(self.service_paths[service_path].interface.ReadValue({}),'big'))
        return heart_rates
    
    def deinit(self):
        pass
