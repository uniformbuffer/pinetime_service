import dbus
import time
from services.device_services import DeviceService
from services.host_services import HostService
from services.interaction_services import InteractionService
from services.host_services import host_services,HostServiceType,Call
from services.interaction_services import interaction_services
from common.utils import filter_by_interface,list_services,list_paired_devices,filter_device_services
from common.notification import Notification,NotificationType
from common.call import CallAnswer
from common.path import device_from_path,PathType
from device import BTDevice

class DeviceConnectionHandler():
    def device_change_handler(self,*args):
        interface = args[0]
        message = args[1]
        if interface == 'org.bluez.Device1' and 'Paired' in message:
            self.callback(message['Paired'],self.device)
    def __init__(self,system_bus,device,callback):
        self.device = device
        self.callback = callback
        self.signal = dbus.Interface(system_bus.get_object('org.bluez', device), 'org.freedesktop.DBus.Properties').connect_to_signal("PropertiesChanged",self.device_change_handler)
    def deinit(self):
        self.signal.remove()

class BTManager():
    def __init__(self):
        self.system_bus = dbus.SystemBus()
        self.session_bus = dbus.SessionBus()

        # Path discovery
        self.discovered_paths = {}
        self.device_added_signal = dbus.Interface(self.system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").connect_to_signal('InterfacesAdded',self.path_added_handler)
        self.device_removed_signal = dbus.Interface(self.system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").connect_to_signal('InterfacesRemoved',self.path_removed_handler)

        # Initializing services
        self.interaction_services = []
        self.host_services = {}
        self.devices = {}
        # Initializing interaction services
        for interaction_service in interaction_services:
            service = interaction_service()
            self.interaction_services.append(service)
            self.on_interaction_service_changed(True,service)

        # Initializing host services
        for service_type in host_services:
            service = host_services[service_type](self.session_bus)
            self.host_services[service_type] = service
            self.on_host_service_changed(True,service)
        
        #if HostServiceType.CALL in self.host_services:
        #    self.host_services[HostServiceType.CALL].add_callback(self.call_callback)

        #if HostServiceType.NOTIFICATION in self.host_services:
        #    self.host_services[HostServiceType.NOTIFICATION].add_callback(self.notification_callback)

        # Enumerating paired devices
        dbus_services = list_services(self.system_bus)
        for device_path in list_paired_devices(self.system_bus):
            print("Device {} paired".format(str(device_path)))
            device_services = filter_device_services(dbus_services,device_path)
            self.discovered_paths[device_path] = DeviceConnectionHandler(self.system_bus,device_path,self.device_connection_handler)
            infos = {}
            device = BTDevice(self.system_bus,self.session_bus,device_path,infos,self.on_device_service_changed)
            self.devices[device.path] = device
            for uuid in device_services:
                device.add_service(device_services[uuid])


    def notify_all(self,notification: Notification):
        for device in self.devices:
            self.devices[device].notify(notification)

    def on_device_service_changed(self,added: bool, device_service: DeviceService):
        if added:
            for interaction_service in self.interaction_services:
                interaction_service.device_service_added(device_service)
            print("Added device service {}({})".format(device_service.__class__.service_type().name,device_service))
        else:
            for interaction_service in self.interaction_services:
                interaction_service.device_service_removed(device_service)
            print("Removed device service {}({})".format(device_service.__class__.service_type().name,device_service))
    def on_host_service_changed(self, added:bool, host_service: HostService):
        if added:
            for interaction_service in self.interaction_services:
                interaction_service.host_service_added(host_service)
            print("Added host service {}({})".format(host_service.__class__.service_type().name,host_service))
        else:
            for interaction_service in self.interaction_services:
                interaction_service.host_service_removed(host_service)
            print("Removed host service {}({})".format(host_service.__class__.service_type().name,host_service))

    def on_interaction_service_changed(self, added:bool, interaction_service: InteractionService):
        pass

    # Callbacks
    def device_connection_handler(self,paired,device_path):
        if paired:
            if device_path not in self.devices:
                print("Device {} paired".format(str(device_path)))
                time.sleep(0.5) #This is required to make bluez stabilize its internal resources
                infos = {}
                self.devices[device_path] = BTDevice(self.system_bus,self.session_bus,device_path,infos,self.on_device_service_changed)
        else:
            if device_path in self.devices:
                print("Device {} unpaired".format(str(device_path)))
                self.devices[device_path].deinit()
                del self.devices[device_path]
    def path_added_handler(self,*args):
        path = args[0]
        interfaces = args[1]
        path_type = PathType.from_path(path)
        if 'org.bluez.Device1' in interfaces and path_type == PathType.DEVICE:
            self.discovered_paths[path] = DeviceConnectionHandler(self.system_bus,path,self.device_connection_handler)
        if 'org.bluez.GattCharacteristic1' in interfaces and path_type == PathType.CHARACTERISTIC:
            device = device_from_path(path)
            if device in self.devices:
                self.devices[device].add_service(path)

    def path_removed_handler(self,*args):
        path = args[0]
        interfaces = args[1]
        path_type = PathType.from_path(path)
        if 'org.bluez.Device1' in interfaces and path_type == PathType.DEVICE:
            if path in self.discovered_paths:
                del self.discovered_paths[path]
        if 'org.bluez.GattCharacteristic1' in interfaces and path_type == PathType.CHARACTERISTIC:
            device = device_from_path(path)
            if device in self.devices:
                self.devices[device].remove_service(path)

    def deinit(self):
        self.device_added_signal.remove()
        self.device_removed_signal.remove()
