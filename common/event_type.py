from enum import Enum
class EventType(Enum):
    UNKNOWN = 0
    CALL = 1
    CALL_ANSWER = 2
    MEDIA_CONTROL = 3
    NOTIFICATION = 4
    HEART_RATE = 5
    BATTERY_LEVEL = 6

