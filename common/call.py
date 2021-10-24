from enum import Enum
class CallAnswer(Enum):
    HANGUP = 0
    ANSWER = 1
    MUTE = 2

class Call():
    def __init__(self,source,number,accept_callback,hangup_callback):
        self.source = source
        self.number = number
        self.accept_callback = accept_callback
        self.hangup_callback = hangup_callback

    def accept(self):
        self.accept_callback()
    def hangup(self):
        self.hangup_callback()
    def __str__():
        return "Incoming call\n{}\n{}".format(self.source,self.number)
