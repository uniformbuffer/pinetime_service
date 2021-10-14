from enum import Enum
import abc
class SystemServiceType(Enum):
    UNKNOWN = ""
    CALL = 0
    MPRIS = 1
    NOTIFICATION = 2
    
    def name(self):
        return self.name
    
    def uuid(self):
        return self.value
    
    @classmethod
    def _missing_(cls, value):
        return DeviceServiceType.UNKNOWN

class SystemService():
    def __init__(self):
        self.callbacks = []
    
    @abc.abstractmethod
    def add_callback(self,callback):
        raise NotImplementedError('`add_callback(self,callback)` method must be defined')
        
    @abc.abstractmethod
    def remove_callback(self,callback):
        raise NotImplementedError('`remove_callback(self,callback)` method must be defined')
        
    @abc.abstractmethod
    def service_type(self):
        raise NotImplementedError('`service_type(self)` method must be defined')


from services.system_services.call import CallService,Call
from services.system_services.notification import NotificationService
from services.system_services.mpris import MPRISService

system_services = {}
system_services[CallService.service_type()] = CallService
system_services[NotificationService.service_type()] = NotificationService
system_services[MPRISService.service_type()] = MPRISService
