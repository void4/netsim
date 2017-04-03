from world import World
from peers import FloodPeer, GraphPeer

world = World(20)
for i in range(50):
    world.add(GraphPeer())
world.run()
