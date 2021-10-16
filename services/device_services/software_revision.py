import dbus
from services.device_services.device_service import DeviceService,DeviceServiceType
from common.path import ServicePath

class SoftwareRevisionService(DeviceService):
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path: str,service_paths: [str]):
        super().__init__()
        self.system_bus = system_bus
        for service_path in service_paths:
            self.add_service_path(service_path)
        print("Initialized device service {} on {}".format(SoftwareRevisionService.service_type().name,device_path))
    
    def service_type():
        return DeviceServiceType.HARDWARE_REVISION

    def add_service_path(self,service_path: str):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        self.service_paths[service_path] = ServicePath(None,None,interface,{})

    def remove_service_path(self,service_path: str):
        if service_path in self.service_paths:
            del self.service_paths[service_path]

    def service_type():
        return DeviceServiceType.SOFTWARE_REVISION

    def add_callback(self,callback):
        pass
    
    def remove_callback(self,callback):
        pass

    def software_revisions(self):
        software_revisions = {}
        for service_path in self.service_paths:
            software_revisions[service_path] = bytearray(self.service_paths[service_path].interface.ReadValue({})).decode("utf-8")
        return software_revisions
    def deinit(self):
        pass
