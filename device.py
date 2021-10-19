import dbus
from services.device_services import search_compatible_service,DeviceServiceType
from common.notification import Notification,NotificationType
from common.path import Path,PathType
from common.utils import get_uuid

class BTDevice():
    def heart_rate_callback(self,value: int):
        print("Heart rate: "+str(value))
    
    def battery_level_callback(self,value: int):
        print("Battery level: "+str(value))
    
    def __init__(self, system_bus, session_bus, device_path, dbus_services,infos):
        self.system_bus = system_bus
        self.session_bus = session_bus
        self.path = device_path
        self.infos = infos
        self.properties = dbus.Interface(self.system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties')
        
        self.services = {}
        for uuid in dbus_services:
            self.add_service(dbus_services[uuid])

        if DeviceServiceType.HEART_RATE in self.services:
            self.services[DeviceServiceType.HEART_RATE].add_callback(self.heart_rate_callback)
        if DeviceServiceType.BATTERY_LEVEL in self.services:
            self.services[DeviceServiceType.BATTERY_LEVEL].add_callback(self.battery_level_callback)

        self.notify(Notification(NotificationType.SIMPLE_ALERT,'Host daemon','Detected and connected'))
    
    def add_service(self,service_path):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        infos = {
            'uuid': interface.Get("org.bluez.GattCharacteristic1","UUID")
        }
        if 'call_event_callback' in self.infos:
            infos['call_event_callback'] = self.infos['call_event_callback']

        service = search_compatible_service(self.system_bus,self.session_bus,str(service_path),infos)
        if service == None:
            return None
        else:
            service_type = service.service_type()
            if service_type not in self.services:
                self.services[service_type] = service(self.system_bus)
            self.services[service_type].add_service_path(service_path,infos)

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

