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
