from enum import Enum


#        value = min(value,100)
#        value = max(value,0)


class SeekOffset():
    def __init__(self,offset: int):
        self.value = offset

class SeekTo():
    def __init__(self,value: int):
        self.value = value

class PlaybackStatus(Enum):
    UNKNOWN = 0
    PLAYING = 1
    PAUSED = 2
    def from_str(status):
        if status == 'Playing':
            return PlaybackStatus.PLAYING
        elif status == 'Stopped' or status == 'Paused':
            return PlaybackStatus.PAUSED
        else:
            print("Unknown value {}".format(status))
            return PlaybackStatus.UNKNOWN

class PlaybackStatusChanged():
    def __init__(self,status: PlaybackStatus):
        self.value = status

class VolumeSet():
    def __init__(self,value: int):
        self.value = value

class VolumeChanged():
    def __init__(self,offset: int):
        self.value = offset

class AppChanged():
    def __init__(self,name: str):
        self.value = name

class MetadataChanged():
    def __init__(self, metadata: {}):
        self.value = metadata

class MediaControlEvent():
    PLAY = PlaybackStatusChanged(PlaybackStatus.PLAYING)
    PAUSE = PlaybackStatusChanged(PlaybackStatus.PAUSED)
    SEEK_FORWARD = SeekOffset(+5000000)
    SEEK_BACKWARD = SeekOffset(-5000000)
    VOLUME_UP = VolumeChanged(+0.05)
    VOLUME_DOWN = VolumeChanged(-0.05)
    APP_CLOSED = AppChanged(None)
    def volume_up(value: int):
        return VolumeChanged(max(value,0))
    def volume_down(value: int):
        return VolumeChanged(min(value,0))
    def seek_forward(value: int):
        return SeekOffset(max(value,0))
    def seek_backward(value: int):
        return SeekOffset(min(value,0))
    def seek_to(value: int):
        return SeekTo(value)
    def app_opened(name: str):
        if name == None:
            raise Exception("Cannot emit APP_OPENED event with None name")
        return AppChanged(name)
    def metadata_changed(metadata: {}):
        return MetadataChanged(metadata)
