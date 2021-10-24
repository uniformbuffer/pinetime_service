
from services.host_services import HostService
from services.device_services import DeviceService

class InteractionService():
    def __init__(self):
        self.enabled = True
        pass
    def host_service_added(self,host_service: HostService):
        pass
    def host_service_removed(self,host_service: HostService):
        pass
    def device_service_added(self,device_service: DeviceService):
        pass
    def device_service_removed(self,device_service: DeviceService):
        pass
    def enabled(self)->bool:
        return self.enabled
    def enable(self,value: bool):
        self.enabled = value
    def name(self)->str:
        pass
    def descriptor(self)->str:
        pass

interaction_services = []


from services.interaction_services.call_notification import CallNotificationService
from services.interaction_services.desktop_notification import DesktopNotificationService
from services.interaction_services.init_notification import InitNotificationService
from services.interaction_services.media_control import MediaControlService

interaction_services.append(CallNotificationService)
interaction_services.append(DesktopNotificationService)
interaction_services.append(InitNotificationService)
interaction_services.append(MediaControlService)
