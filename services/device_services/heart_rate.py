import dbus
from services.device_services.device_service import DeviceService,DeviceServiceType

class HeartRateService(DeviceService):
    def heart_rate_handler(self,interface,dictionary,unused):
        if 'Value' in dictionary:
            value = int.from_bytes(bytearray(dictionary['Value']), "big")
            for callback in self.callbacks:
                callback(value)
    
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path,service_path):
        super().__init__()
        self.heart_rate_listener = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').connect_to_signal("PropertiesChanged",self.heart_rate_handler)
        self.interface = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        if len(self.callbacks) > 0:
            self.interface.StartNotify()
    
    def service_type():
        return DeviceServiceType.HEART_RATE
    
    def add_callback(self,callback):
        self.callbacks.append(callback)
        if len(self.callbacks) == 1:
            print("{} notification started".format(HeartRateService.service_type()))
            self.interface.StartNotify()
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)
        if len(self.callbacks) == 0:
            print("{} notification stopped".format(HeartRateService.service_type()))
            self.interface.StopNotify()

    def heart_rate(self):
        return int.from_bytes(bytearray(self.interface.ReadValue({})),'big')
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.heart_rate_listener.remove()
        if len(self.callbacks) > 0:
            self.interface.StopNotify()
