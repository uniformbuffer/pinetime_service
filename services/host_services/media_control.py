import dbus
from services.host_services import HostService,HostServiceType
from common.event_type import EventType
from common.path import ServicePath
from common.media_control import MediaControlEvent,PlaybackStatus,PlaybackStatusChanged

def convert_metadata(metadata: {})->{}:
    new_metadata = {}
    if 'xesam:artist' in metadata:
        new_metadata['artist'] = ','.join(metadata['xesam:artist'])
    if 'xesam:album' in metadata:
        new_metadata['album'] = str(metadata['xesam:album'])
    if 'xesam:title' in metadata:
        new_metadata['track'] = str(metadata['xesam:title'])
    if 'mpris:length' in metadata:
        new_metadata['length'] = int(metadata['mpris:length'])
    return new_metadata

class MPRISApplication():
    def wrapped_callback(self,interface,message,unused):
        if 'Volume' in message:
            self.volume = message['Volume']
        self.callback(interface,message,unused)
    def __init__(self,session_bus: dbus.SessionBus, name: str,callback):
        self.callback = callback
        self.interface = dbus.Interface(session_bus.get_object(name,'/org/mpris/MediaPlayer2'), 'org.mpris.MediaPlayer2.Player')
        self.properties = dbus.Interface(session_bus.get_object(name,'/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties')
        self.signal = self.properties.connect_to_signal("PropertiesChanged",self.wrapped_callback)
        self.volume = self.properties.Get('org.mpris.MediaPlayer2.Player','Volume')
    def interface_name(self)->str:
        return self.interface.dbus_interface
    def get_properties(self)->{}:
        return self.properties.GetAll('org.mpris.MediaPlayer2.Player')
    def seek_offset(self,offset):
        self.interface.Seek(offset)
    def seek_to(self,position):
        self.interface.Position(position)
    def get_position(self)->int:
        return int(self.properties.Get('org.mpris.MediaPlayer2.Player','Position'))
    def next(self):
        self.interface.Next()
    def previous(self):
        self.interface.Previous()
    def play_pause(self):
        self.interface.PlayPause()
    def play(self):
        self.interface.Play()
    def pause(self):
        self.interface.Pause()
    def get_volume(self)->float:
        return self.volume
    def volume_offset(self, offset: float):
        volume = self.get_volume() + offset
        volume = min(volume,1.0)
        volume = max(volume,0.0)
        self.properties.Set('org.mpris.MediaPlayer2.Player','Volume',volume)
    def set_volume(self,volume: float):
        volume = min(volume,1.0)
        volume = max(volume,0.0)
        self.properties.Set('org.mpris.MediaPlayer2.Player','Volume',volume)
    def get_metadata(self)->{}:
        return convert_metadata(self.properties.Get('org.mpris.MediaPlayer2.Player','Metadata'))
    def get_playback_status(self)->PlaybackStatus:
        return PlaybackStatus.from_str(self.properties.Get('org.mpris.MediaPlayer2.Player','PlaybackStatus'))

class MediaControlService(HostService):
    def mpris_handler(self,name,old_owner,new_owner):
        if name.startswith('org.mpris.MediaPlayer2'):
            if old_owner == '' and new_owner != '':
                event = MediaControlEvent.app_opened(new_owner)
                callbacks = self.get_callbacks(EventType.MEDIA_CONTROL)
                for index in callbacks:
                    callbacks[index](event)
                application = MPRISApplication(self.session_bus,new_owner,self.mpris_property_change_handler)
                self.applications.append(application)

            if new_owner == '' and old_owner != '':
                event = MediaControlEvent.APP_CLOSED
                callbacks = self.get_callbacks(EventType.MEDIA_CONTROL)

                if len(self.applications) > 0:
                    del self.applications[-1]

                if len(self.applications) > 0:
                    event = MediaControlEvent.app_opened(self.applications[-1].interface_name())
                else:
                    event = MediaControlEvent.APP_CLOSED
                for index in callbacks:
                    callbacks[index](event)

    def mpris_property_change_handler(self,interface,message,unused):
        callbacks = self.get_callbacks(EventType.MEDIA_CONTROL)
        events = []
        if 'PlaybackStatus' in message:
            events.append(PlaybackStatusChanged(PlaybackStatus.from_str(message['PlaybackStatus'])))
        if 'Position' in message:
            events.append(MediaControlEvent.seek_to(message['Position']))
        if 'Metadata' in message:
            events.append(MediaControlEvent.metadata_changed(convert_metadata(message['Metadata'])))
        for event in events:
            for index in callbacks:
                callbacks[index](event)
    def __init__(self,session_bus: dbus.SessionBus):
        super().__init__()
        self.session_bus = session_bus
        self.mpris_listener = self.session_bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').connect_to_signal("NameOwnerChanged",self.mpris_handler)
        self.applications = []
        for service in session_bus.list_names():
            if service.startswith('org.mpris.MediaPlayer2'):
                self.applications.append(MPRISApplication(self.session_bus,service,self.mpris_property_change_handler))
                break

    def service_type():
        return HostServiceType.MEDIA_CONTROL
    def get_properties(self)->{}:
        return self.applications[-1].get_properties()
    def seek_offset(self,offset):
        if len(self.applications) > 0:
            self.applications[-1].seek_offset(offset)
    def seek_to(self,position):
        if len(self.applications) > 0:
            self.applications[-1].seek_to(position)
    def next(self):
        if len(self.applications) > 0:
            self.applications[-1].next()
    def previous(self):
        if len(self.applications) > 0:
            self.applications[-1].previous()
    def play_pause(self):
        if len(self.applications) > 0:
            self.applications[-1].play_pause()
    def play(self):
        if len(self.applications) > 0:
            self.applications[-1].play()
    def pause(self):
        if len(self.applications) > 0:
            self.applications[-1].pause()
    def get_volume(self)->float:
        if len(self.applications) > 0:
            return self.applications[-1].get_volume()
        else:
            return None
    def volume_offset(self, offset: float):
        if len(self.applications) > 0:
            self.applications[-1].volume_offset(offset)
    def set_volume(self,volume: float):
        if len(self.applications) > 0:
            self.applications[-1].set_volume(volume)
    def get_metadata(self)->{}:
        if len(self.applications) > 0:
            return self.applications[-1].get_metadata()
        else:
            return None
    def get_playback_status(self)->PlaybackStatus:
        if len(self.applications) > 0:
            return self.applications[-1].get_playback_status()
        else:
            return None

