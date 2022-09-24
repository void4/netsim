from time import sleep

import pygame

import ptext

from world import World
from peers import FloodPeer, GraphPeer, EmptyPeer


pygame.init()
pygame.display.set_caption("NetSim")
font = pygame.font.SysFont(None, 24)

w = 512#800
h = 512#600

radius = 300

screen = pygame.display.set_mode((w,h))

color = (255, 255, 255)

world = World(w,h,radius)
for i in range(5):
	world.add(GraphPeer())#GraphPeer())

world.init()

peer_width = 20
peer_height = 20


i = 0
running = True
while running:
	screen.fill(color)

	for peer in world.peers:
		x,y = peer.pos
		pygame.draw.ellipse(screen, (200, 200, 200), pygame.Rect(x-world.radius, y-world.radius, world.radius*2, world.radius*2), width=1)

	for event in world.connectivity:
		pygame.draw.line(screen, (0,0,0), event[0].pos, event[1].pos, width=1)

	for event in world.events:
		pygame.draw.line(screen, (0,255,0), event[0].pos, event[1].pos, width=5)

	for peer in world.peers:
		x,y = peer.pos

		pygame.draw.rect(screen, (100, 100, 255), pygame.Rect(x-peer_width//2, y-peer_height//2, peer_width, peer_height))

		#img = font.render(, True, (0,0,0))
		#screen.blit(img, (x-peer_width//2, y-peer_height//2))
		nodeinfo = "sent: "+str(peer.seq)+"\nrecvbuf: "+str(len(peer.recvarr))
		ptext.draw(nodeinfo, pos=(x-peer_width//2, y-peer_height//2), color=(0,0,0), fontsize=12)

	i += 1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	pygame.display.flip()

	world.update()

	sleep(0.1)



#world.run()
