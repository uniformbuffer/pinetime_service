import dbus
import abc
from services.device_services import DeviceService,DeviceServiceType
from common.path import ServicePath

class FirmwareRevisionService(DeviceService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    @abc.abstractmethod
    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        raise NotImplementedError('`__init__(self,system_bus: dbus.SystemBus,device_path: str)` method must be defined')

    @abc.abstractmethod
    def firmware_revisions(self):
        raise NotImplementedError('`__init__(self,system_bus: dbus.SystemBus,device_path: str)` method must be defined')

    def service_type():
        return DeviceServiceType.FIRMWARE_REVISION
