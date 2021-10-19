import dbus
from enum import Enum
from common.notification import Notification,NotificationType
from common.path import device_from_path,PathType
from common.call import CallAnswer
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
    def __init__(self, request, event):
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
        self.path_tuples = {}
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
        if uuid == "00020001-78fc-48fe-8e23-433b3a1942d0":
            return True
        elif service_type == "00002a46":
            return True
        else:
            return False

    def add_service_path(self,service_path: str, infos: {}):
        super().add_service_path(service_path,infos)
        new_service = self.service_paths[service_path]
        new_service.properties = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')

        device = device_from_path(service_path)
        if device not in self.path_tuples:
            self.path_tuples[device] = NotificationServicePaths(None,None)
        self.path_tuples[device].add_path(service_path,infos)

        if 'call_event_callback' in infos:
            self.add_callback(infos['call_event_callback'])

    def notify(self, notification: Notification):
        for device_path in self.path_tuples:
            notification_service_tuple = self.path_tuples[device_path]
            # InfiniTime convert the first 3 bytes (8 bits) into an unsigned int that specify what kind of message it has received
            # Currently the available types are all the same except for CALL
            prefix = InfiniTimeNotificationType.from_notification(notification.type).value[0].to_bytes(3,byteorder='little')
            message = prefix + str(notification).encode('utf_8')

            signal = None
            event_service = None
            request_service = None
            if notification_service_tuple.event != None:
                event_service = self.service_paths[notification_service_tuple.event]
            if notification_service_tuple.request != None:
                request_service = self.service_paths[notification_service_tuple.request]

            if event_service != None:
                event_service.signal = event_service.properties.connect_to_signal("PropertiesChanged",self.call_handler)
                self.current_call_event_service =  event_service
                self.current_call_event_service.interface.StartNotify()
            if request_service != None:
                request_service.interface.WriteValue(message,{})

    def call_handler(self,interface,message,unused):
        if 'Value' in message and self.current_call_event_service != None:
            call_event = CallAnswer(int.from_bytes(bytearray(message['Value']), "big"))
            for callback in self.callbacks:
                callback(call_event)
            self.current_call_event_service.interface.StopNotify()
            self.current_call_event_service.signal.remove()
            self.current_call_event_service = None

