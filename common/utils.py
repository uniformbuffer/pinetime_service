import dbus
def filter_by_interface(objects, interface_name):
    """ filters the objects based on their support
        for the specified interface """
    result = {}
    for path in objects.keys():
        interfaces = objects[path]
        for interface in interfaces.keys():
            if interface == interface_name:
                result[path] = objects[path]
    return result

def get_uuid(system_bus,service_path):
    print("Detecting UUID on {}".format(service_path))
    interface = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
    uuid = interface.Get("org.bluez.GattCharacteristic1","UUID")

def list_services(system_bus):
    dbus_services = {}
    bluez_objects = dbus.Interface(system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").GetManagedObjects()
    for service_path in filter_by_interface(bluez_objects, "org.bluez.GattCharacteristic1"):
        interface = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties')
        uuid = interface.Get("org.bluez.GattCharacteristic1","UUID")
        dbus_services[uuid] = service_path
    return dbus_services

def list_paired_devices(system_bus):
    paired_devices = []
    bluez_objects = dbus.Interface(system_bus.get_object('org.bluez', '/'), "org.freedesktop.DBus.ObjectManager").GetManagedObjects()
    for device_path in filter_by_interface(bluez_objects, "org.bluez.Device1"):
        # Check if device is paired
        interface = dbus.Interface(system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties')
        if interface.Get("org.bluez.Device1", "Paired"):
            paired_devices.append(device_path)
    return paired_devices

def filter_device_services(dbus_services,device_path:str):
    device_services = {}
    for uuid in dbus_services:
        path = dbus_services[uuid]
        if path.startswith(device_path):
            device_services[uuid] = path
    return device_services
