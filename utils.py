from time import time

def distance(a, b):
    return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5

# Object which is true once after <interval> seconds
class Every:
    def __init__(self, interval):
        self.interval = interval
        self.lasttime = time()

    def __bool__(self):
        current = time()
        if current-self.lasttime>=self.interval:
            self.lasttime = current
            return True
        return False
