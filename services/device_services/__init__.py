from enum import Enum
import abc
import dbus
from common.path import ServicePath,PathType

class DeviceServiceType(Enum):
    UNKNOWN = ""
    NOTIFICATION = "00002a46"
    HEART_RATE = "00002a37"
    BATTERY_LEVEL = "00002a19"
    SOFTWARE_REVISION = "00002a28"
    HARDWARE_REVISION = "00002a27"
    FIRMWARE_REVISION = "00002a26"

    @classmethod
    def _missing_(cls, value):
        return DeviceServiceType.UNKNOWN

class DeviceService():
    @abc.abstractmethod
    def __init__(self,system_bus: dbus.SystemBus):
        self.system_bus = system_bus
        self.callbacks = []
        self.service_paths = {}

    @abc.abstractmethod
    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        raise NotImplementedError('`compatible(self,path: str)` method must be defined')

    @abc.abstractmethod
    def service_type(self):
        raise NotImplementedError('`service_type(self)` method must be defined')

    def add_service_path(self,service_path: str, infos: {}):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        self.service_paths[service_path] = ServicePath(None,None,interface,infos)
        print("Initialized device service {} on {}".format(self.__class__.service_type().name,service_path))

    def remove_service_path(self,service_path: str):
        if service_path in self.service_paths:
            del self.service_paths[service_path]

    def add_callback(self,callback):
        self.callbacks.append(callback)

    def remove_callback(self,callback):
        self.callbacks.remove(callback)

    def deinit(self):
        pass


from services.device_services.notification.infinitime import InfinitimeNotificationService




from services.device_services.battery_level.generic import GenericBatteryLevelService
from services.device_services.notification.generic import GenericNotificationService
from services.device_services.heart_rate.generic import GenericHeartRateService
from services.device_services.firmware_revision.generic import GenericFirmwareRevisionService
from services.device_services.hardware_revision.generic import GenericHardwareRevisionService
from services.device_services.software_revision.generic import GenericSoftwareRevisionService

device_services = [
    InfinitimeNotificationService,
    GenericBatteryLevelService,
    GenericNotificationService,
    GenericHeartRateService,
    GenericFirmwareRevisionService,
    GenericHardwareRevisionService,
    GenericSoftwareRevisionService
]

def search_compatible_service(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {}):
    for service in device_services:
        if service.compatible(system_bus,session_bus,service_path,infos):
            return service
    return None

