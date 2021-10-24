import dbus
from enum import Enum
from common.notification import Notification,NotificationType
from common.path import device_from_path,PathType,ServicePath
from services.device_services.notification import NotificationService


class NotificationServiceType(Enum):
    UNKNOWN = 0
    REQUEST = 1
    EVENT = 2

    def from_uuid(uuid: str):
        service_type = uuid.split('-')[0]
        if uuid == "00020001-78fc-48fe-8e23-433b3a1942d0":
            return NotificationServiceType.EVENT
        elif service_type == "00002a46":
            return NotificationServiceType.REQUEST
        else:
            return NotificationServiceType.UNKNOWN

class NotificationServicePaths():
    def __init__(self, system_bus, request, event):
        self.request = request
        self.event = event
    def add_path(self,service_path: str,infos: {}):
        notification_service_type = NotificationServiceType.from_uuid(infos['uuid'])
        if self.event == None and notification_service_type == NotificationServiceType.EVENT:
            self.event = service_path
        elif self.request == None and notification_service_type == NotificationServiceType.REQUEST:
            self.request = service_path

class InfiniTimeNotificationType(Enum):
    SIMPLE_ALERT = 0x00,
    EMAIL = 0x01,
    NEWS = 0x02,
    CALL = 0x03,
    MISSED_CALL = 0x04,
    MMS_SMS = 0x05,
    VOICE_MAIL = 0x06,
    SCHEDULE = 0x07,
    HIGH_PRIORITIZED_ALERT = 0x08,
    INSTANT_MESSAGE = 0x09,

    def from_notification(notification_type: NotificationType):
        if notification_type == NotificationType.SIMPLE_ALERT:
            return InfiniTimeNotificationType.SIMPLE_ALERT
        elif notification_type == NotificationType.EMAIL:
            return InfiniTimeNotificationType.EMAIL
        elif notification_type == NotificationType.NEWS:
            return InfiniTimeNotificationType.NEWS
        elif notification_type == NotificationType.CALL:
            return InfiniTimeNotificationType.CALL
        elif notification_type == NotificationType.MISSED_CALL:
            return InfiniTimeNotificationType.MISSED_CALL
        elif notification_type == NotificationType.MMS_SMS:
            return InfiniTimeNotificationType.MMS_SMS
        elif notification_type == NotificationType.VOICE_MAIL:
            return InfiniTimeNotificationType.VOICE_MAIL
        elif notification_type == NotificationType.SCHEDULE:
            return InfiniTimeNotificationType.SCHEDULE
        elif notification_type == NotificationType.HIGH_PRIORITIZED_ALERT:
            return InfiniTimeNotificationType.HIGH_PRIORITIZED_ALERT
        elif notification_type == NotificationType.INSTANT_MESSAGE:
            return InfiniTimeNotificationType.INSTANT_MESSAGE

class InfinitimeNotificationService(NotificationService):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)
        self.service_paths = {}
        self.current_call_event_service = None

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'device_path' in infos:
            device_path = infos['device_path']
        else:
            device_path = device_from_path(service_path)
        if device_path == None:
            return False

        if 'alias' in infos:
            alias = infos['alias']
        else:
            alias = dbus.Interface(system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.Device1", "Alias")
        if not alias.lower().startswith("infinitime"):
            return False

        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")

        service_type = uuid.split('-')[0]
        if service_type == "00002a46":
            return True
        else:
            return False

    def add_service_path(self,service_path: str, infos: {}):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        self.service_paths[service_path] = ServicePath(None,None,interface,infos)

    def remove_service_path(self,service_path: str):
        if service_path in self.service_paths:
            del self.service_paths[service_path]

    def list_service_paths(self)->[str]:
        list(self.service_paths.keys())

    def notify(self, notification: Notification):
        for device_path in self.service_paths:
            service_path = self.service_paths[device_path]
            # InfiniTime convert the first 3 bytes (8 bits) into an unsigned int that specify what kind of message it has received
            # Currently the available types are all the same except for CALL
            notification_value = 0
            message = notification_value.to_bytes(3,byteorder='little') + str(notification).encode('utf_8')
            service_path.interface.WriteValue(message,{})

    def list_service_paths(self)->[str]:
        list(self.service_paths.keys())

