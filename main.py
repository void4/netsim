from world import World
from peers import FloodPeer, GraphPeer

import pygame
from time import sleep

pygame.init()
pygame.display.set_caption("NetSim")
font = pygame.font.SysFont(None, 24)

w = 800
h = 600

radius = 150

screen = pygame.display.set_mode((w,h))

color = (255, 255, 255)

world = World(w,h,radius)
for i in range(50):
	world.add(GraphPeer())

world.init()


i = 0
running = True
while running:
	screen.fill(color)

	for peer in world.peers:
		x,y = peer.pos

		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x, y, 20, 20))
		pygame.draw.ellipse(screen, (200, 200, 200), pygame.Rect(x-world.radius, y-world.radius, world.radius*2, world.radius*2), width=1)

		img = font.render(str(peer.seq), True, (0,0,0))
		screen.blit(img, (x, y))

	for event in world.connectivity:
		pygame.draw.line(screen, (0,0,0), event[0].pos, event[1].pos, width=1)

	for event in world.events:
		pygame.draw.line(screen, (0,255,0), event[0].pos, event[1].pos, width=5)

	i += 1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	pygame.display.flip()

	world.update()

	sleep(0.1)



#world.run()
