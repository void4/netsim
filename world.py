import stackless
from time import time
from random import random, randint
import os
from PIL import Image, ImageDraw
from pyqtree import Index

os.makedirs("anim", exist_ok=True)

from utils import distsquared, Every

class World:
    def __init__(self, size=256, runtime=100):
        self.size = size
        self.runtime = runtime
        self.peers = []
        self.csend = 0
        self.crecv = 0
        self.every = Every(1)
        self.it = 0

        self.totalobjectives = 0
        self.clearedobjectives = 0
        self.objectives = []

    def add(self, peer):
        peer.pos = [random()*self.size for i in range(2)]
        self.peers.append(peer)

    def env(self):
        for peer in self.peers:
            flag = {"type":"flag", "hop":0, "target":randint(0,len(self.peers)-1), "data":random()}
            peer.flagin.append(flag)
            self.objectives.append(flag)
        self.totalobjectives = len(self.objectives)

    def check(self):
        for obj in self.objectives:
            target = self.peers[obj["target"]]
            for flag in target.flagout:
                if obj["data"] == flag["data"]:
                    print("Received flag after %i hops" % obj["hop"])
                    self.clearedobjectives += 1
                    self.objectives.remove(obj)
                    target.flagout.remove(flag)

        #count false flags at the end

    def run(self):
        self.env()
        start = time()
        #while time()<start+self.runtime:
        while self.it<100:
            self.update()

    def update(self):
        simstart = time()
        index = Index((0,0,self.size,self.size))
        for peer in self.peers:#randomize order
            index.insert(peer.pid, (peer.pos[0],peer.pos[1],peer.pos[0]+1,peer.pos[1]+1))

        for peer in self.peers:
            peer.task.insert()
            stackless.run(1000)#run for n seconds?#randint(500,3000))
            peer.task.remove()
            self.csend += len(peer.sendarr)
            bb = 50
            for pid in index.intersect((peer.pos[0]-bb,peer.pos[1]-bb,peer.pos[0]+1+bb,peer.pos[1]+1+bb)):
                peer2 = self.peers[pid]
                dist = distsquared(peer.pos, peer2.pos, self.size, self.size)
                if peer2 != peer and dist<50:#10/dist>random():
                    for msg in peer.sendarr:
                        peer2.recv(msg)#aah, all packets sent at once! not realistic
                        self.crecv += 1
            peer.sendarr = []
            #peer.pos = [(p+(random()-0.5)*0.2)%self.size for p in peer.pos]

        simend = time()
        if self.every:
            #os.system("clear")
            self.cbacklog = sum([len(peer.recvarr) for peer in self.peers])
            self.check()
            print("ITER:{} FPS:{} Sent:{} Recv:{} Backlog:{} Flags:{} Cleared:{}".format(
                self.it, int(1/(simend-simstart)), self.csend, self.crecv, self.cbacklog, self.totalobjectives, self.clearedobjectives))


            img = Image.new("RGB", (self.size, self.size))
            draw = ImageDraw.Draw(img)
            for peer in self.peers:
                color = (0,0,255)
                if peer.pid == 0:
                    color = (255,255,255)
                color = (min(255,len(peer.recvarr)),0,255)
                draw.rectangle(peer.pos+[peer.pos[0]+1,peer.pos[1]+1], color)
            img.save("anim/%i.png" % self.it)

            self.it += 1
