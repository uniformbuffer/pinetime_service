import abc
import dbus
from enum import Enum
from common.path import ServicePath,PathType
from common.callback import CallbackManager

class DeviceServiceType(Enum):
    UNKNOWN = 0
    NOTIFICATION = 1
    HEART_RATE = 2
    BATTERY_LEVEL = 3
    SOFTWARE_REVISION = 4
    HARDWARE_REVISION = 5
    FIRMWARE_REVISION = 6
    MEDIA_CONTROL = 7
    CALL = 8

    @classmethod
    def _missing_(cls, value):
        return DeviceServiceType.UNKNOWN

class DeviceService(CallbackManager):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__()
        self.system_bus = system_bus
        self.service_paths = {}

    @abc.abstractmethod
    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        raise NotImplementedError('`compatible(self,path: str)` method must be defined')

    @abc.abstractmethod
    def service_type(self):
        raise NotImplementedError('`service_type(self)` method must be defined')

    @abc.abstractmethod
    def add_service_path(self,service_path: str, infos: {}):
        raise NotImplementedError('`service_type(self)` method must be defined')
        #interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        ##self.service_paths[service_path] = ServicePath(None,None,interface,infos)
        print("Initialized device service {} on {}".format(self.__class__.service_type().name,service_path))
    @abc.abstractmethod
    def remove_service_path(self,service_path: str):
        raise NotImplementedError('`service_type(self)` method must be defined')
        #if service_path in self.service_paths:
        #    del self.service_paths[service_path]

    @abc.abstractmethod
    def list_service_paths(self)->[str]:
        raise NotImplementedError('`service_type(self)` method must be defined')

    def deinit(self):
        pass


from services.device_services.notification.infinitime import InfinitimeNotificationService
from services.device_services.call.infinitime import InfinitimeCallService
from services.device_services.media_control.infinitime import InfinitimeMediaControlService

from services.device_services.battery_level.generic import GenericBatteryLevelService
from services.device_services.notification.generic import GenericNotificationService
from services.device_services.heart_rate.generic import GenericHeartRateService
from services.device_services.firmware_revision.generic import GenericFirmwareRevisionService
from services.device_services.hardware_revision.generic import GenericHardwareRevisionService
from services.device_services.software_revision.generic import GenericSoftwareRevisionService

device_services = [
    InfinitimeMediaControlService,
    InfinitimeNotificationService,
    InfinitimeCallService,
    GenericBatteryLevelService,
    GenericNotificationService,
    GenericHeartRateService,
    GenericFirmwareRevisionService,
    GenericHardwareRevisionService,
    GenericSoftwareRevisionService
]

def search_compatible_services(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->[DeviceService]:
    services = []
    for service in device_services:
        if service.compatible(system_bus,session_bus,service_path,infos):
            services.append(service)
    return services

