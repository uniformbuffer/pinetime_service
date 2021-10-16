import dbus
from services.system_services.system_service import system_services,SystemServiceType,Call
from common.filters import filter_by_interface
from common.notification import Notification,NotificationType
from common.path import device_from_path,PathType
from device import BTDevice

class DeviceConnectionHandler():
    def device_change_handler(self,interface,message,unused):
        if 'Paired' in message:
            self.callback(message['Paired'],self.device)
    def __init__(self,system_bus,device,callback):
        print("Listening for {} pairing".format(device))
        self.device = device
        self.callback = callback
        self.signal = dbus.Interface(system_bus.get_object('org.bluez', device), 'org.freedesktop.DBus.Properties').connect_to_signal("PropertiesChanged",self.device_change_handler)
    def __exit__(self, exc_type, exc_value, traceback):
        self.signal.remove()

class BTManager():
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
        
        self.discovered_paths = {}
        self.device_added_signal = dbus.Interface(self.system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").connect_to_signal('InterfacesAdded',self.path_added_handler)
        self.device_removed_signal = dbus.Interface(self.system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").connect_to_signal('InterfacesRemoved',self.path_removed_handler)

        # Enumerating paired devices
        self.devices = {}
        
        dbus_services = self.list_services()

        for dbus_device in self.list_paired_devices():
            device_services = self.filter_device_services(dbus_services,dbus_device)
            print("Discovered device {}".format(dbus_device))
            device = BTDevice(self.system_bus,self.session_bus,dbus_device,device_services)
            self.devices[device.path] = device

    def notify_all(self,notification: Notification):
        for device in self.devices:
            self.devices[device].notify(notification)
    def list_services(self):
        dbus_services = {}
        bluez_objects = dbus.Interface(self.system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").GetManagedObjects()
        for service_path in filter_by_interface(bluez_objects, "org.bluez.GattCharacteristic1"):
            interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
            uuid = interface.Get("org.bluez.GattCharacteristic1","UUID")
            dbus_services[uuid] = service_path
        return dbus_services
    def list_paired_devices(self):
        paired_devices = []
        bluez_objects = dbus.Interface(self.system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").GetManagedObjects()
        for dbus_device in filter_by_interface(bluez_objects, "org.bluez.Device1"):
            # Check if device is paired
            interface = dbus.Interface(self.system_bus.get_object('org.bluez', dbus_device), 'org.freedesktop.DBus.Properties')
            if interface.Get("org.bluez.Device1", "Paired"):
                paired_devices.append(dbus_device)
        return paired_devices
    def filter_device_services(self,dbus_services,dbus_device:str):
        device_services = {}
        for uuid in dbus_services:
            path = dbus_services[uuid]
            if path.startswith(dbus_device):
                device_services[uuid] = path
        return device_services
    # Callbacks
    def device_connection_handler(self,paired,device_path):
        if paired:
            print(str(device_path) + " paired")
            dbus_services = self.list_services()
            device_services = self.filter_device_services(dbus_services,device_path)
            self.devices[device_path] = BTDevice(self.system_bus,self.session_bus,device_path,device_services)
            print(self.devices)
        else:
            print(str(device_path) + " disconnected")
            if device_path in self.devices:
                del self.devices[device_path]
    def path_added_handler(self,*args):
        path = args[0]
        path_type = PathType.from_path(path)
        if path_type == PathType.DEVICE:
            print("Device discovered: "+str(path))
            self.discovered_paths[path] = DeviceConnectionHandler(self.system_bus,path,self.device_connection_handler)
        if path_type == PathType.CHARACTERISTIC:
            print("Service discovered: "+str(path))
            device = device_from_path(path)
            if device in self.devices:
                self.devices[device].add_service(path)

    def path_removed_handler(self,*args):
        path = args[0]
        path_type = PathType.from_path(path)
        if path_type == PathType.CHARACTERISTIC:
            device = device_from_path(path)
            if device in self.devices:
                self.devices[device].remove_service(path)

    def call_callback(self,call: Call):
        source = "Incoming call from {}".format(call.source)
        body = call.number
        notification = Notification(NotificationType.CALL,source,body)
        self.notify_all(notification)
    def notification_callback(self,notification: Notification):
        self.notify_all(notification)
    
