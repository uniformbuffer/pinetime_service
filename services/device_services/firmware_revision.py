import dbus
from services.device_services.device_service import DeviceService,DeviceServiceType

class FirmwareRevisionService(DeviceService):
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path,service_path):
        super().__init__()
        self.interface = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
    
    def service_type():
        return DeviceServiceType.FIRMWARE_REVISION
    
    def add_callback(self,callback):
        pass
    
    def remove_callback(self,callback):
        pass
    
    def firmware_revision(self):
        return bytearray(self.interface.ReadValue({})).decode("utf-8")
