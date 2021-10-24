import dbus
from common.path import ServicePath,PathType
from services.device_services.hardware_revision import HardwareRevisionService
from common.path import ServicePath

class GenericHardwareRevisionService(HardwareRevisionService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")
        service_type = uuid.split('-')[0]
        if service_type == "00002a27":
            return True
        else:
            return False

    def add_service_path(self,service_path: str, infos: {}):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        self.service_paths[service_path] = ServicePath(None,None,interface,infos)

    def remove_service_path(self,service_path: str):
        if service_path in self.service_paths:
            del self.service_paths[service_path]

    def list_service_paths(self)->[str]:
        list(self.service_paths.keys())

    def hardware_revisions(self):
        hardware_revisions = {}
        for service_path in self.service_paths:
            hardware_revisions[service_path] = bytearray(self.service_paths[service_path].interface.ReadValue({})).decode("utf-8")
        return hardware_revisions

