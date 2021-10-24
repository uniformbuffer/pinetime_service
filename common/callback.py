from common.event_type import EventType
class CallbackHandle():
    def __init__(self,manager, index: int):
        self.manager = manager
        self.index = index
    def release(self):
        self.manager.remove_callback(self.index)

class CallbackManager():
    def __init__(self):
        self.counter = 0
        self.callbacks = {}

    def add_callback(self,event_type: EventType,callback)->CallbackHandle:
        self.callbacks[self.counter] = (event_type,callback)
        callback_handle = CallbackHandle(self,self.counter)
        self.counter = self.counter + 1
        return callback_handle

    def remove_callback(self,index: int):
        del self.callbacks[index]

    def get_callbacks(self,event_type: EventType)->{}:
        filtered_callbacks = {}
        if event_type == None:
            return self.callbacks
        else:
            return {index:callback[1] for (index,callback) in self.callbacks.items() if event_type == callback[0]}

