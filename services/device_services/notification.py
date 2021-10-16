import dbus
from enum import Enum
from services.device_services.device_service import DeviceService,DeviceServiceType
from common.notification import Notification,NotificationType
from common.path import ServicePath

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



class NotificationService(DeviceService):
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path: str,service_paths: [str]):
        super().__init__()
        self.system_bus = system_bus
        self.device_path = device_path
        for service_path in service_paths:
            self.add_service_path(service_path)
        print("Initialized device service {} on {}".format(NotificationService.service_type().name,device_path))

    def service_type():
        return DeviceServiceType.HARDWARE_REVISION

    def add_service_path(self,service_path: str):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        members = {
            'infinitime': dbus.Interface(self.system_bus.get_object('org.bluez', self.device_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.Device1", "Alias").lower().startswith("infinitime")
        }
        self.service_paths[service_path] = ServicePath(None,None,interface,members)

    def remove_service_path(self,path: str):
        if path in self.service_paths:
            del self.service_paths[path]
    
    def service_type():
        return DeviceServiceType.NOTIFICATION
    
    def add_callback(self,callback):
        pass
    
    def remove_callback(self,callback):
        pass
    
    def notify(self, notification: Notification):
        for service_path in self.service_paths:
            service = self.service_paths[service_path]

            if service.members['infinitime']:
                # InfiniTime convert the first 3 bytes (8 bits) into an unsigned int that specify what kind of message it has received
                # Currently the available types are all the same except for CALL
                prefix = InfiniTimeNotificationType.from_notification(notification.type).value[0].to_bytes(3,byteorder='little')
                message = prefix + str(notification).encode('utf_8')
                return service.interface.WriteValue(message,{})
            else:
                message = str(notification).encode('utf_8')
                return service.interface.WriteValue(message,{})

    def deinit(self):
        pass
