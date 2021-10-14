from enum import Enum

class NotificationType(Enum):
    SIMPLE_ALERT = 0,
    EMAIL = 1,
    NEWS = 2,
    CALL = 3,
    MISSED_CALL = 4,
    MMS_SMS = 5,
    VOICE_MAIL = 6,
    SCHEDULE = 7,
    HIGH_PRIORITIZED_ALERT = 8,
    INSTANT_MESSAGE = 9,

class Notification():
    def __init__(self,type,source,body):
        self.type = type
        self.source = source
        self.body = body
    def __str__(self):
        return self.source+'\n'+self.body

