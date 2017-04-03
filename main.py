from world import World
from peers import FloodPeer, GraphPeer

world = World(1)
for i in range(10):
    world.add(GraphPeer())
world.run()
