

class Pendings():
    def __init__(self):
        self.pendings = {}
    def add_pendings(self,key,value):
        if key in self.pendings:
            self.pendings[key].append(value)
        else:
            self.pendings[key] = [value]
    def replace_pendings(self,key,value):
        self.pendings[key] = [value]
    def pop_pendings(self,key)->[]:
        if key in self.pendings:
            values = self.pendings[key]
            del self.pendings[key]
            return values
        else:
            return []
