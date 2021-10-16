import dbus
from services.device_services.device_service import device_services,DeviceServiceType
from common.notification import Notification,NotificationType
from common.path import Path,PathType
from common.utils import get_uuid

class BTDevice():
    def heart_rate_callback(self,value: int):
        print("Heart rate: "+str(value))
    
    def battery_level_callback(self,value: int):
        print("Battery level: "+str(value))
    
    def __init__(self, system_bus, session_bus, device_path, dbus_services):
        self.system_bus = system_bus
        self.session_bus = session_bus
        self.path = device_path
        self.properties = dbus.Interface(self.system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties')
        
        self.services = {}
        for uuid in dbus_services:
            service_type = DeviceServiceType(uuid.split('-')[0])
            if service_type in device_services:
                if service_type not in self.services:
                    service_paths = [dbus_services[uuid]]
                    if service_type in device_services:
                        self.services[service_type] = device_services[service_type](self.services,self.system_bus,device_path,service_paths)
                else:
                    self.services[service_type].add_service_path(dbus_services[uuid])
        
        if DeviceServiceType.HEART_RATE in self.services:
            self.services[DeviceServiceType.HEART_RATE].add_callback(self.heart_rate_callback)
        if DeviceServiceType.BATTERY_LEVEL in self.services:
            self.services[DeviceServiceType.BATTERY_LEVEL].add_callback(self.battery_level_callback)

        self.notify(Notification(NotificationType.SIMPLE_ALERT,'Host daemon','Detected and connected'))
    
    def add_service(self,service_path):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        uuid = interface.Get("org.bluez.GattCharacteristic1","UUID")
        service_type = DeviceServiceType(uuid)
        if service_type in self.services:
            self.services[service_type].add_service_path(service_path)
        else:
            if service_type in device_services:
                self.services[service_type] = device_services[service_type](self.services,self.system_bus,self.path,[service_path])
    def remove_service(self,service_path):
        for service_type in self.services:
            self.services[service_type].remove_service_path(service_path)
    def alias(self):
        return str(self.properties.Get("org.bluez.Device1", "Alias"))
    def address(self):
        return str(self.properties.Get("org.bluez.Device1", "Address"))
    def software_revision(self):
        if DeviceServiceType.SOFTWARE_REVISION in self.services:
            return self.services[DeviceServiceType.SOFTWARE_REVISION].software_revision()
        else:
            None
    def hardware_revision(self):
        if DeviceServiceType.HARDWARE_REVISION in self.services:
            return self.services[DeviceServiceType.HARDWARE_REVISION].hardware_revision()
        else:
            None
    def firmware_revision(self):
        if DeviceServiceType.FIRMWARE_REVISION in self.services:
            return self.services[DeviceServiceType.FIRMWARE_REVISION].firmware_revision()
        else:
            None
    def battery(self):
        if DeviceServiceType.BATTERY_LEVEL in self.services:
            return self.services[DeviceServiceType.BATTERY_LEVEL].battery()
        else:
            None
    def notify(self,notification: Notification):
        if DeviceServiceType.NOTIFICATION in self.services:
            return self.services[DeviceServiceType.NOTIFICATION].notify(notification)
    def heart_rate(self):
        if DeviceServiceType.HEART_RATE in self.services:
            return self.services[DeviceServiceType.HEART_RATE].heart_rate()
        else:
            None
    def deinit(self):
        for service in self.services:
            self.services[service].deinit()

