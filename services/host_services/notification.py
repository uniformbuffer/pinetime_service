import dbus
from common.notification import Notification,NotificationType
from common.event_type import EventType
from services.host_services import HostService,HostServiceType

class NotificationService(HostService):
    def notification_handler(self,bus,message):
        if message.get_member() == "Notify":
            args = message.get_args_list();
            source = args[0]
            body = args[3]
            notification = Notification(NotificationType.SIMPLE_ALERT,source,body)
            callbacks = self.get_callbacks(EventType.NOTIFICATION)
            for index in callbacks:
                callbacks[index](notification)

    def __init__(self,session_bus: dbus.SessionBus):
        super().__init__()
        session_bus.add_match_string_non_blocking("type='method_call',interface='org.freedesktop.Notifications',member='Notify',eavesdrop='true'")
        session_bus.add_message_filter(self.notification_handler)

    def service_type():
        return HostServiceType.NOTIFICATION
