import dbus
from enum import Enum
from services.device_services.device_service import DeviceService,DeviceServiceType
from common.notification import Notification,NotificationType

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



class NotificationService():
    def __init__(self,device_services,system_bus: dbus.SystemBus,device_path,service_path):
        super().__init__()
        self.interface = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
        self.infinitime = dbus.Interface(system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.Device1", "Alias").lower().startswith("infinitime")
    
    def service_type():
        return DeviceServiceType.NOTIFICATION
    
    def add_callback(self,callback):
        pass
    
    def remove_callback(self,callback):
        pass
    
    def notify(self, notification: Notification):
        if self.infinitime:
            # InfiniTime convert the first 3 bytes (8 bits) into an unsigned int that specify what kind of message it has received
            # Currently the available types are all the same except for CALL
            prefix = InfiniTimeNotificationType.from_notification(notification.type).value[0].to_bytes(3,byteorder='little')
            message = prefix + str(notification).encode('utf_8')
            return self.interface.WriteValue(message,{})
        else:
            message = str(notification).encode('utf_8')
            return self.interface.WriteValue(message,{})
