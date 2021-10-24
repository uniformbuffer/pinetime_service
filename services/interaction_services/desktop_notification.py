from services.interaction_services import InteractionService
from services.host_services import HostService,HostServiceType
from services.device_services import DeviceService,DeviceServiceType
from common.notification import Notification

class DesktopNotificationService(InteractionService):
    def __init__(self):
        self.host_notification_service = None
        self.device_notification_services = []
    def host_service_added(self,host_service: HostService):
        if host_service.__class__.service_type() == HostServiceType.NOTIFICATION and self.host_notification_service == None:
            host_service.add_callback("notification_event",self.notification_callback)
            self.host_notification_service = host_service

    def host_service_removed(self,host_service: HostService):
        if self.host_notification_service == host_service:
            self.host_notification_service = None

    def device_service_added(self,device_service: DeviceService):
        if device_service.__class__.service_type() == DeviceServiceType.NOTIFICATION:
            self.device_notification_services.append(device_service)


    def device_service_removed(self,device_service: DeviceService):
        self.device_notification_services.remove(device_service)

    def notification_callback(self,notification: Notification):
        for device_notification_service in self.device_notification_services:
            device_notification_service.notify(notification)
