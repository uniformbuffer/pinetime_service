import dbus
from services.device_services.device_service import DeviceService,DeviceServiceType

class BatteryLevelService(DeviceService):
    def battery_level_handler(self,interface,dictionary,unused):
        if 'Value' in dictionary:
            value = int.from_bytes(bytearray(dictionary['Value']), "big")
            for callback in self.callbacks:
                callback(value)
    
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path,service_path):
        super().__init__()
        
        self.properties = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        self.battery_level_listener = self.properties.connect_to_signal("PropertiesChanged",self.battery_level_handler)
        self.interface = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
    
    def battery(self):
        return int(self.properties.Get("org.bluez.Battery1", "Percentage"))
    
    def service_type():
        return DeviceServiceType.BATTERY_LEVEL
    
    def add_callback(self,callback):
        self.callbacks.append(callback)
        if len(self.callbacks) == 1:
            print("{} notification started".format(BatteryLevelService.service_type()))
            self.interface.StartNotify()
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)
        if len(self.callbacks) == 0:
            print("{} notification stopped".format(BatteryLevelService.service_type()))
            self.interface.StopNotify()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.heart_rate_listener.remove()
        for callback in self.callbacks:
            self.callbacks.remove(callback)
