from enum import Enum
import abc
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
    def __init__(self):
        self.callbacks = []
        self.service_paths = {}

    @abc.abstractmethod
    def add_service_path(self,path: str):
        raise NotImplementedError('`add_service_path(self,path: str)` method must be defined')

    @abc.abstractmethod
    def remove_service_path(self,path: str):
        raise NotImplementedError('`remove_service_path(self,path: str)` method must be defined')
    
    @abc.abstractmethod
    def add_callback(self,callback):
        raise NotImplementedError('`add_callback(self,callback)` method must be defined')
        
    @abc.abstractmethod
    def remove_callback(self,callback):
        raise NotImplementedError('`remove_callback(self,callback)` method must be defined')
        
    @abc.abstractmethod
    def service_type(self):
        raise NotImplementedError('`service_type(self)` method must be defined')

device_services = {}

from services.device_services.battery_level import BatteryLevelService
from services.device_services.notification import NotificationService
from services.device_services.heart_rate import HeartRateService
from services.device_services.firmware_revision import FirmwareRevisionService
from services.device_services.hardware_revision import HardwareRevisionService
from services.device_services.software_revision import SoftwareRevisionService

device_services[BatteryLevelService.service_type()] = BatteryLevelService
device_services[HeartRateService.service_type()] = HeartRateService
device_services[NotificationService.service_type()] = NotificationService
device_services[SoftwareRevisionService.service_type()] = SoftwareRevisionService
device_services[HardwareRevisionService.service_type()] = HardwareRevisionService
device_services[FirmwareRevisionService.service_type()] = FirmwareRevisionService
