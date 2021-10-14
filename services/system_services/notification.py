import dbus
from services.system_services.system_service import SystemService,SystemServiceType
from common.notification import Notification,NotificationType

class NotificationService(SystemService):
    def notification_handler(self,bus,message):
        if message.get_member() == "Notify":
            args = message.get_args_list();
            source = args[0]
            body = args[3]
            notification = Notification(NotificationType.SIMPLE_ALERT,source,body)
            for callback in self.callbacks:
                callback(notification)
    
    def __init__(self,session_bus: dbus.SessionBus):
        super().__init__()
        session_bus.add_match_string_non_blocking("type='method_call',interface='org.freedesktop.Notifications',member='Notify',eavesdrop='true'")
        session_bus.add_message_filter(self.notification_handler)
    
    def service_type():
        return SystemServiceType.NOTIFICATION
    
    def add_callback(self,callback):
        self.callbacks.append(callback)
    
    def remove_callback(self,callback):
        self.callbacks.remove(callback)
