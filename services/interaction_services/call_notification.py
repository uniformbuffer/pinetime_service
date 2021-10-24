from services.interaction_services import InteractionService
from services.host_services import HostService,HostServiceType
from services.device_services import DeviceService,DeviceServiceType
from common.call import Call,CallAnswer
from common.event_type import EventType

class CallNotificationService(InteractionService):
    def __init__(self):
        self.host_call_service = None
        self.device_call_services = []
    def host_service_added(self,host_service: HostService):
        if host_service.__class__.service_type() == HostServiceType.CALL and self.host_call_service == None:
            host_service.add_callback(EventType.CALL,self.call_notification_callback)
            self.host_call_service = host_service
            if len(self.device_call_services) > 0:
                for (index,(service,callback)) in enumerate(device_call_services):
                    if callback == None:
                        device_call_services[index][1] = service.add_callback(EventType.CALL,self.call_event_callback)

    def host_service_removed(self,host_service: HostService):
        if self.host_call_service == host_service:
            self.host_call_service = None

    def device_service_added(self,device_service: DeviceService):
        if device_service.__class__.service_type() == DeviceServiceType.CALL:
            if self.host_call_service != None:
                callback_handle = device_service.add_callback(EventType.CALL,self.call_event_callback)
            else:
                callback_handle = None
            self.device_call_services.append((device_service,callback_handle))

    def device_service_removed(self,device_service: DeviceService):
        self.device_call_services.remove(device_service)

    def call_notification_callback(self,call: Call):
        if self.host_call_service != None:
            for (call_service,callback) in self.device_call_services:
                call_service.notify_call(call)
    def call_event_callback(self,call_event: CallAnswer):
        if self.host_call_service != None:
            if call_event == CallAnswer.ANSWER:
                self.host_call_service.accept()
            elif call_event == CallAnswer.HANGUP:
                self.host_call_service.hangup()
            else:
                pass
