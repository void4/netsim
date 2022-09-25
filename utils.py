from time import time
from random import random

def distance(a, b):
    return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5

# Object which is true once after <interval> seconds
class Every:
    def __init__(self, interval, randomoffset=None):
        self.interval = interval
        self.lasttime = time()
        if randomoffset is not None:
            self.lasttime -= random()*randomoffset

    def __bool__(self):
        current = time()
        if current-self.lasttime>=self.interval:
            self.lasttime = current
            return True
        return False
