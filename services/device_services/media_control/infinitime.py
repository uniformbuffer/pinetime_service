import dbus
from enum import Enum
from common.notification import Notification,NotificationType
from common.path import device_from_path,PathType
from common.media_control import PlaybackStatus,MediaControlEvent
from common.event_type import EventType
from common.pending import Pendings
from services.device_services.media_control import MediaControlService

class MediaControlServicePathType(Enum):
    UNKNOWN = 0
    EVENT = 1
    STATUS = 2
    ARTIST = 3
    ALBUM = 4
    TRACK = 5
    POSITION = 6
    LENGTH = 7

    def from_uuid(uuid: str):
        if uuid == "00000001-78fc-48fe-8e23-433b3a1942d0":
            return MediaControlServicePathType.EVENT
        elif uuid == "00000002-78fc-48fe-8e23-433b3a1942d0":
            return MediaControlServicePathType.STATUS
        elif uuid == "00000003-78fc-48fe-8e23-433b3a1942d0":
            return MediaControlServicePathType.ARTIST
        elif uuid == "00000004-78fc-48fe-8e23-433b3a1942d0":
            return MediaControlServicePathType.TRACK
        elif uuid == "00000005-78fc-48fe-8e23-433b3a1942d0":
            return MediaControlServicePathType.ALBUM
        elif uuid == "00000006-78fc-48fe-8e23-433b3a1942d0":
            return MediaControlServicePathType.POSITION
        elif uuid == "00000007-78fc-48fe-8e23-433b3a1942d0":
            return MediaControlServicePathType.LENGTH
        else:
            return MediaControlServicePathType.UNKNOWN

class InfinitimeMediaControlService(MediaControlService,Pendings):
    def __init__(self,system_bus: dbus.SystemBus):
        super().__init__(system_bus)
        Pendings.__init__(self)
        self.service_paths = {}
        self.event_signal = None
        self.event_interface = None
        self.status_interface = None
        self.artist_interface = None
        self.album_interface = None
        self.track_interface = None
        self.position_interface = None
        self.length_interface = None

        # Setting initial status
        self.set_playback_status(PlaybackStatus.PAUSED)
        self.set_artist(" ")
        self.set_album(" ")
        self.set_track(" ")
        self.set_position(0)
        self.set_length(0)

    def compatible(system_bus: dbus.SystemBus, session_bus: dbus.SessionBus, service_path: str, infos: {})->bool:
        if 'alias' in infos:
            alias = infos['alias']
        else:
            device_path = device_from_path(service_path)
            alias = dbus.Interface(system_bus.get_object('org.bluez', device_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.Device1", "Alias")
        if not alias.lower().startswith("infinitime"):
            return False

        if 'uuid' in infos:
            uuid = infos['uuid']
        else:
            uuid = dbus.Interface(system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').Get("org.bluez.GattCharacteristic1","UUID")

        if MediaControlServicePathType.from_uuid(uuid) != MediaControlServicePathType.UNKNOWN:
            return True
        else:
            return False

    def add_service_path(self,service_path: str, infos: {}):
        media_control_service_path_type = MediaControlServicePathType.from_uuid(infos['uuid'])
        if media_control_service_path_type == MediaControlServicePathType.EVENT and self.event_interface == None:
            self.event_signal = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.freedesktop.DBus.Properties').connect_to_signal("PropertiesChanged",self.media_control_event_handler)
            interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            interface.StartNotify()
            self.event_interface = interface
        elif media_control_service_path_type == MediaControlServicePathType.STATUS and self.status_interface == None:
            self.status_interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            for command in self.pop_pendings("status"):
                command()
        elif media_control_service_path_type == MediaControlServicePathType.ARTIST and self.artist_interface == None:
            self.artist_interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            for command in self.pop_pendings("artist"):
                command()
        elif media_control_service_path_type == MediaControlServicePathType.ALBUM and self.album_interface == None:
            self.album_interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            for command in self.pop_pendings("album"):
                command()
        elif media_control_service_path_type == MediaControlServicePathType.TRACK and self.track_interface == None:
            self.track_interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            for command in self.pop_pendings("track"):
                command()
        elif media_control_service_path_type == MediaControlServicePathType.POSITION and self.position_interface == None:
            self.position_interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            for command in self.pop_pendings("position"):
                command()
        elif media_control_service_path_type == MediaControlServicePathType.LENGTH and self.length_interface == None:
            self.length_interface = dbus.Interface(self.system_bus.get_object('org.bluez', service_path), 'org.bluez.GattCharacteristic1')
            for command in self.pop_pendings("length"):
                command()

    def remove_service_path(self,service_path: str):
        if service_path == self.event_interface.object_path:
            self.event_signal.remove()
            self.event_signal = None
            self.event_interface.StopNotify()
            self.event_interface = None
        if service_path == self.status_interface.object_path:
            self.status_interface = None
        if service_path == self.artist_interface.object_path:
            self.artist_interface = None
        if service_path == self.album_interface.object_path:
            self.album_interface = None
        if service_path == self.track_interface.object_path:
            self.track_interface = None

    def list_service_paths(self)->[str]:
        service_paths = []
        if self.event_interface != None:
            service_paths.append(self.event_interface.object_path)
        if self.status_interface != None:
            service_paths.append(self.status_interface.object_path)
        if self.artist_interface != None:
            service_paths.append(self.artist_interface.object_path)
        if self.album_interface != None:
            service_paths.append(self.album_interface.object_path)
        if self.track_interface != None:
            service_paths.append(self.track_interface.object_path)
        return service_paths

    def set_playback_status(self, status: PlaybackStatus):
        if status == PlaybackStatus.PLAYING:
            status_value = 1
        elif status == PlaybackStatus.PAUSED:
            status_value = 0
        else:
            return None
        if self.status_interface != None:
            self.status_interface.WriteValue(status_value.to_bytes(1,byteorder='little'),{})
        else:
            self.replace_pendings("status",lambda: self.set_playback_status(status))
    def set_artist(self, artist: str):
        if self.artist_interface != None:
            self.artist_interface.WriteValue(artist.encode('utf_8'),{})
        else:
            self.replace_pendings("artist",lambda: self.set_artist(artist))

    def set_album(self, album: str):
        if self.album_interface != None:
            self.album_interface.WriteValue(album.encode('utf_8'),{})
        else:
            self.replace_pendings("album",lambda: self.set_album(album))
    def set_track(self, track: str):
        if self.track_interface != None:
            self.track_interface.WriteValue(track.encode('utf_8'),{})
        else:
            self.replace_pendings("track",lambda: self.set_track(track))
    def set_position(self, position: int):
        if self.position_interface != None:
            self.position_interface.WriteValue(position.to_bytes(4,byteorder='big'),{})
        else:
            self.replace_pendings("position",lambda: self.set_position(position))
    def set_length(self, length: int):
        if self.length_interface != None:
            self.length_interface.WriteValue(length.to_bytes(4,byteorder='big'),{})
        else:
            self.replace_pendings("length",lambda: self.set_length(length))
    def media_control_event_handler(self,interface,message,unused):
        if 'Value' in message:
            value = int.from_bytes(bytearray(message['Value']), "big")
            if value == 0:
                event = MediaControlEvent.PLAY
            elif value == 1:
                event = MediaControlEvent.PAUSE
            #elif value == 224:
                #pass
                #event = MediaControlEvent.APP_OPENED
            elif value == 3:
                event = MediaControlEvent.SEEK_FORWARD
            elif value == 4:
                event = MediaControlEvent.SEEK_BACKWARD
            elif value == 5:
                event = MediaControlEvent.VOLUME_UP
            elif value == 6:
                event = MediaControlEvent.VOLUME_DOWN
            else:
                event = None
            if event != None:
                callbacks = self.get_callbacks(EventType.MEDIA_CONTROL)
                for index in callbacks:
                    callbacks[index](event)

