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
