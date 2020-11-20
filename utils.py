from time import time

# Calculates distance in wrapped 2d-space
def wrappedDistanceSquared(a, b, width, height):
    dx = a[0]-b[0]
    if dx>width//2:
        dx = width-dx
    dy = a[1]-b[1]
    if dy>height//2:
        dy = height-dy
    return dx*dx+dy*dy

def wrappedDistance(a,b,width,height):
    return (wrappedDistanceSquared(a,b,width,height))**0.5

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
