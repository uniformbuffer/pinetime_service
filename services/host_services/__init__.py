import abc
from enum import Enum
from common.callback import CallbackManager
class HostServiceType(Enum):
    UNKNOWN = ""
    CALL = 0
    MPRIS = 1
    NOTIFICATION = 2
    MEDIA_CONTROL = 3

    @classmethod
    def _missing_(cls, value):
        return DeviceServiceType.UNKNOWN

class HostService(CallbackManager):
    @abc.abstractmethod
    def service_type(self):
        raise NotImplementedError('`service_type(self)` method must be defined')


from services.host_services.call import CallService,Call
from services.host_services.notification import NotificationService
from services.host_services.media_control import MediaControlService

host_services = {}
host_services[CallService.service_type()] = CallService
host_services[NotificationService.service_type()] = NotificationService
host_services[MediaControlService.service_type()] = MediaControlService
