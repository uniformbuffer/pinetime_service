import dbus
from services.system_services.system_service import system_services,SystemServiceType,Call
from common.filters import filter_by_interface
from common.notification import Notification
from device import BTDevice
from common.notification import Notification,NotificationType

class BTManager():
    def call_callback(self,call: Call):
        source = "Incoming call from {}".format(call.source)
        body = call.number
        notification = Notification(NotificationType.CALL,source,body)
        self.notify_all(notification)
    def notification_callback(self,notification: Notification):
        self.notify_all(str(notification))
    
    def __init__(self):
        self.system_bus = dbus.SystemBus()
        self.session_bus = dbus.SessionBus()
        
        # Initializing system services
        self.services = {}
        for service_type in system_services:
            print("Initialized system service {}".format(service_type))
            self.services[service_type] = system_services[service_type](self.session_bus)
        
        if SystemServiceType.CALL in self.services:
            self.services[SystemServiceType.CALL].add_callback(self.call_callback)
        
        if SystemServiceType.NOTIFICATION in self.services:
            self.services[SystemServiceType.NOTIFICATION].add_callback(self.notification_callback)
        
        # Enumerating paired devices
        self.devices = {}
        
        dbus_services = {}
        bluez_objects = dbus.Interface(self.system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").GetManagedObjects()
        for service_path in filter_by_interface(bluez_objects, "org.bluez.GattCharacteristic1"):
            interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
            uuid = interface.Get("org.bluez.GattCharacteristic1","UUID")
            dbus_services[uuid] = service_path
        
        for dbus_device in filter_by_interface(bluez_objects, "org.bluez.Device1"):
            # Check if device is paired
            interface = dbus.Interface(self.system_bus.get_object('org.bluez', dbus_device), 'org.freedesktop.DBus.Properties')
            if interface.Get("org.bluez.Device1", "Paired"):
                # Filter device services
                device_services = {}
                for uuid in dbus_services:
                    path = dbus_services[uuid]
                    if path.startswith(dbus_device):
                        device_services[uuid] = path
                
                print("Discovered device {}".format(dbus_device))
                device = BTDevice(self.system_bus,self.session_bus,dbus_device,device_services)
                self.devices[device.path()] = device
    
    def notify_all(self,notification: Notification):
        for device in self.devices:
            self.devices[device].notify(notification)

