from world import World
from peers import FloodPeer

world = World()
for i in range(500):
    world.add(FloodPeer())
world.run()
