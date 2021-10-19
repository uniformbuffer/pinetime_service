import dbus
from common.path import ServicePath,PathType
from services.device_services.notification import NotificationService
from common.notification import Notification,NotificationType

class GenericNotificationService(NotificationService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")
        service_type = uuid.split('-')[0]
        if service_type == "00002a46":
            return True
        else:
            return False

    def notify(self, notification: Notification):
        for service_path in self.service_paths:
            service = self.service_paths[service_path]
            message = str(notification).encode('utf_8')
            service.interface.WriteValue(message,{})

