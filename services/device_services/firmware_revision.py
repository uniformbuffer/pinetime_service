import dbus
from services.device_services.device_service import DeviceService,DeviceServiceType
from common.path import ServicePath

class FirmwareRevisionService(DeviceService):
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path: str,service_paths: [str]):
        super().__init__()
        self.system_bus = system_bus
        for service_path in service_paths:
            self.add_service_path(service_path)
        print("Initialized device service {} on {}".format(FirmwareRevisionService.service_type().name,device_path))
    
    def service_type():
        return DeviceServiceType.FIRMWARE_REVISION

    def add_service_path(self,service_path: str):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        self.service_paths[service_path] = ServicePath(None,None,interface,{})

    def remove_service_path(self,service_path: str):
        if service_path in self.service_paths:
            del self.service_paths[service_path]

    def add_callback(self,callback):
        pass
    
    def remove_callback(self,callback):
        pass
    
    def firmware_revisions(self):
        firmware_revisions = {}
        for service_path in self.service_paths:
            firmware_revisions[service_path] = bytearray(self.service_paths[service_path].interface.ReadValue({})).decode("utf-8")
        return firmware_revisions
    def deinit(self):
        pass
