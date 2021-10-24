import dbus
from services.device_services import search_compatible_services,DeviceService,DeviceServiceType
from common.notification import Notification,NotificationType
from common.path import Path,PathType
from common.utils import get_uuid

class BTDevice():
    def heart_rate_callback(self,value: int):
        print("Heart rate: "+str(value))
    
    def battery_level_callback(self,value: int):
        print("Battery level: "+str(value))
    
    def __init__(self, system_bus, session_bus, device_path,infos, device_service_callback):
        self.system_bus = system_bus
        self.session_bus = session_bus
        self.path = device_path
        self.infos = infos
        self.device_service_callback = device_service_callback
        self.properties = dbus.Interface(self.system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties')
        self.services = {}

        if DeviceServiceType.HEART_RATE in self.services:
            self.services[DeviceServiceType.HEART_RATE].add_callback(self.heart_rate_callback)
        if DeviceServiceType.BATTERY_LEVEL in self.services:
            self.services[DeviceServiceType.BATTERY_LEVEL].add_callback(self.battery_level_callback)

        #self.notify(Notification(NotificationType.SIMPLE_ALERT,'Host daemon','Detected and connected'))
    
    def add_service(self,service_path):
        interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        infos = {
            'uuid': interface.Get("org.bluez.GattCharacteristic1","UUID")
        }
        if 'call_event_callback' in self.infos:
            infos['call_event_callback'] = self.infos['call_event_callback']

        services = search_compatible_services(self.system_bus,self.session_bus,str(service_path),infos)
        for service in services:
            service_type = service.service_type()
            is_new = False
            if service_type not in self.services:
                self.services[service_type] = service(self.system_bus)
                is_new = True
            self.services[service_type].add_service_path(service_path,infos)
            if is_new:
                self.device_service_callback(True,self.services[service_type])

    def remove_service(self,service_path):
        for service_type in self.services:
            service = self.services[service_type]
            service.remove_service_path(service_path)
            if len(service.list_service_paths()) == 0:
                del self.services[service_type]
                self.device_service_callback(False,service)
    def service(self,service_type: DeviceServiceType)->DeviceService:
        if service_type in self.services:
            return self.services[service_type]
        else:
            None

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

