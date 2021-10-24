from services.interaction_services import InteractionService
from services.host_services import HostService
from services.device_services import DeviceService,DeviceServiceType
from common.notification import Notification,NotificationType

class InitNotificationService(InteractionService):
    def __init__(self):
        pass
    def host_service_added(self,host_service: HostService):
        pass

    def host_service_removed(self,host_service: HostService):
        pass

    def device_service_added(self,device_service: DeviceService):
        if device_service.__class__.service_type() == DeviceServiceType.NOTIFICATION:
            device_service.notify(Notification(NotificationType.SIMPLE_ALERT,"Bluetooth daemon","Connected and ready"))

    def device_service_removed(self,device_service: DeviceService):
        pass

