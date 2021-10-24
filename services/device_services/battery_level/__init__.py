import dbus
import abc
from services.device_services import DeviceService,DeviceServiceType
from common.path import ServicePath

class BatteryLevelService(DeviceService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    @abc.abstractmethod
    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        raise NotImplementedError('`compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool` method must be defined')

    @abc.abstractmethod
    def add_service_path(self,service_path: str, infos: {}):
        raise NotImplementedError('`service_type(self)` method must be defined')

    @abc.abstractmethod
    def remove_service_path(self,service_path: str):
        raise NotImplementedError('`service_type(self)` method must be defined')

    @abc.abstractmethod
    def list_service_paths(self)->[str]:
        raise NotImplementedError('`service_type(self)` method must be defined')

    @abc.abstractmethod
    def battery_levels(self)->{}:
        raise NotImplementedError('`battery_levels(self)->{}` method must be defined')

    def service_type():
        return DeviceServiceType.BATTERY_LEVEL

