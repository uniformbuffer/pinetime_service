import dbus
from common.path import ServicePath,PathType
from services.device_services.firmware_revision import FirmwareRevisionService
from common.path import ServicePath

class GenericFirmwareRevisionService(FirmwareRevisionService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")
        service_type = uuid.split('-')[0]
        if service_type == "00002a26":
            return True
        else:
            return False

    def firmware_revisions(self):
        firmware_revisions = {}
        for service_path in self.service_paths:
            firmware_revisions[service_path] = bytearray(self.service_paths[service_path].interface.ReadValue({})).decode("utf-8")
        return firmware_revisions

