import math
from services.interaction_services import InteractionService
from services.host_services import HostService,HostServiceType
from services.device_services import DeviceService,DeviceServiceType
from common.media_control import MediaControlEvent,SeekOffset,SeekTo,VolumeChanged,MetadataChanged,PlaybackStatusChanged,AppChanged,PlaybackStatus
from common.event_type import EventType

class MediaControlService(InteractionService):
    def __init__(self):
        self.host_media_control_service = None
        self.device_media_control_services = []
    def host_service_added(self,host_service: HostService):
        if host_service.__class__.service_type() == HostServiceType.MEDIA_CONTROL and self.host_media_control_service == None:
            host_service.add_callback(EventType.MEDIA_CONTROL,self.host_media_control_callback)
            self.host_media_control_service = host_service
            if len(self.device_media_control_services) > 0:
                for (index,(service,callback)) in enumerate(device_media_control_services):
                    if callback == None:
                        device_media_control_services[index][1] = service.add_callback(EventType.MEDIA_CONTROL,self.device_media_control_callback)

    def host_service_removed(self,host_service: HostService):
        if self.host_media_control_service == host_service:
            self.host_media_control_service = None

    def device_service_added(self,device_service: DeviceService):
        if device_service.__class__.service_type() == DeviceServiceType.MEDIA_CONTROL:
            if self.host_media_control_service != None:
                callback_handle = device_service.add_callback(EventType.MEDIA_CONTROL,self.device_media_control_callback)
                metadata = MediaControlEvent.metadata_changed(self.host_media_control_service.get_metadata())
                self.host_media_control_callback(metadata)

                #if metadata != None:
                #    if 'artist' in metadata:
                #        device_service.set_artist(metadata['artist'])
                #    if 'album' in metadata:
                #        device_service.set_album(metadata['album'])
                #    if 'track' in metadata:
                #        device_service.set_track(metadata['track'])
                #playback_status = self.host_media_control_service.get_playback_status()
                #device_service.set_playback_status(playback_status)
            else:
                callback_handle = None
            self.device_media_control_services.append((device_service,callback_handle))

    def device_service_removed(self,device_service: DeviceService):
        self.device_media_control_services.remove(device_service)

    def host_media_control_callback(self,event: MediaControlEvent):
        if event.__class__ == MetadataChanged:
            for media_control_service in self.device_media_control_services:
                media_control_service = media_control_service[0]
                if 'artist' in event.value:
                    media_control_service.set_artist(event.value['artist'])
                if 'album' in event.value:
                    media_control_service.set_album(event.value['album'])
                if 'track' in event.value:
                    media_control_service.set_track(event.value['track'])
                if 'length' in event.value:
                    media_control_service.set_length(int(event.value['length'] / 1000000))
        elif event.__class__ == PlaybackStatusChanged:
            for media_control_service in self.device_media_control_services:
                media_control_service = media_control_service[0]
                media_control_service.set_playback_status(event.value)
        elif event.__class__ == SeekTo:
            for media_control_service in self.device_media_control_services:
                media_control_service = media_control_service[0]
                position = int(math.ceil(event.value / 1000000))
                media_control_service.set_position(position)
        elif event.__class__ == AppChanged:
            if event.value == None:
                metadata = {
                    'artist': ' ',
                    'album': ' ',
                    'track': ' ',
                    'length': 0,
                }
                self.host_media_control_callback(MediaControlEvent.metadata_changed(metadata))
                self.host_media_control_callback(MediaControlEvent.PAUSE)
                self.host_media_control_callback(MediaControlEvent.seek_to(0))

    def device_media_control_callback(self,event: MediaControlEvent):
        if event == MediaControlEvent.PLAY:
            self.host_media_control_service.play()
        elif event == MediaControlEvent.PAUSE:
            self.host_media_control_service.pause()
        elif event.__class__ == SeekOffset:
            self.host_media_control_service.seek_offset(event.value)
        elif event.__class__ == VolumeChanged:
            self.host_media_control_service.volume_offset(event.value)
