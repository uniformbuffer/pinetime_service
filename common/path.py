from enum import Enum
class PathType(Enum):
    UNKNOWN = 0,
    BUS = 1,
    ADAPTER = 2,
    DEVICE = 3,
    SERVICE = 4,
    CHARACTERISTIC = 5,
    DESCRIPTOR = 6

    def from_path(path: str):
        pieces = path.split('/')
        if pieces[-1].startswith('desc'):
            return PathType.DESCRIPTOR
        elif pieces[-1].startswith('char'):
            return PathType.CHARACTERISTIC
        elif pieces[-1].startswith('service'):
            return PathType.SERVICE
        elif pieces[-1].startswith('dev'):
            return PathType.DEVICE
        elif pieces[-1].startswith('hci'):
            return PathType.ADAPTER
        else:
            return PathType.BUS

def device_from_path(path: str):
    pieces = path.split('/')
    if len(pieces) < 5:
        return None
    else:
        separator = '/'
        return separator.join(pieces[0:5])

class Path():
    def __init__(self,path: str):
        self.path = path
        separator = '/'
        path_pieces = self.path.split(separator)
        self.type = PathType.UNKNOWN
        if len(path_pieces) > 2:
            self.bus = Path(separator.join(path_pieces[0:3]))
            self.type = PathType.BUS
        else:
            self.bus = None
        if len(path_pieces) > 3:
            self.adapter = Path(separator.join(path_pieces[0:4]))
            self.type = PathType.ADAPTER
        else:
            self.adapter = None
        if len(path_pieces) > 4:
            self.device = Path(separator.join(path_pieces[0:5]))
            self.type = PathType.DEVICE
        else:
            self.device = None
        if len(path_pieces) > 5:
            self.service = Path(separator.join(path_pieces[0:6]))
            self.type = PathType.SERVICE
        else:
            self.service = None
        if len(path_pieces) > 6:
            self.characteristic = Path(separator.join(path_pieces[0:7]))
            self.type = PathType.CHARACTERISTIC
        else:
            self.characteristic = None
        if len(path_pieces) > 7:
            self.descriptor = Path(separator.join(path_pieces[0:8]))
            self.type = PathType.DESCRIPTOR
        else:
            self.descriptor = None
    def from_bus(path: str):
        self.path = path
        self.type = PathType.BUS
    def from_adapter(path: str):
        self.path = path
        self.type = PathType.ADAPTER
    def from_device(path: str):
        self.path = path
        self.type = PathType.DEVICE
    def from_service(path: str):
        self.path = path
        self.type = PathType.SERVICE
    def from_characteristic(path: str):
        self.path = path
        self.type = PathType.CHARACTERISTIC
    def from_descriptor(path: str):
        self.path = path
        self.type = PathType.DESCRIPTOR
    def __str__(self):
        return self.path
