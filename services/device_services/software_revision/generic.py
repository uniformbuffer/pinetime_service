import dbus
from common.path import ServicePath,PathType
from services.device_services.software_revision import SoftwareRevisionService

class GenericSoftwareRevisionService(SoftwareRevisionService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")
        service_type = uuid.split('-')[0]
        if service_type == "00002a28":
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

    def software_revisions(self):
        software_revisions = {}
        for service_path in self.service_paths:
            software_revisions[service_path] = bytearray(self.service_paths[service_path].interface.ReadValue({})).decode("utf-8")
        return software_revisions

