import stackless
from time import time
from random import random, randint
import os
from PIL import Image, ImageDraw
from pyqtree import Index

os.makedirs("anim", exist_ok=True)

from utils import wrappedDistance, Every

class World:
    def __init__(self, width=800, height=600, radius=300,runtime=100):
        self.width = width
        self.height = height
        self.radius = radius
        self.runtime = runtime
        self.peers = []
        self.csend = 0
        self.crecv = 0
        self.every = Every(1)
        self.it = 0

        self.totalobjectives = 0
        self.clearedobjectives = 0
        self.objectives = []

        self.flagbandwidth = None
        self.flagavglag = None

        self.doneobjectives = []

        self.connectivity = []
        self.events = []

    def add(self, peer):
        peer.pos = [random()*self.width, random()*self.height]
        self.peers.append(peer)

    def env(self):
        for peer in self.peers:
            flag = {"type":"flag", "hop":0, "target":randint(0,len(self.peers)-1), "data":random(), "creation":self.it}
            peer.flagin.append(flag)
            self.objectives.append(flag)
        self.totalobjectives = len(self.objectives)

    def check(self):
        now = time()
        for obj in self.objectives:
            target = self.peers[obj["target"]]
            for flag in target.flagout:
                if obj["data"] == flag["data"]:
                    print("Received flag after %i hops" % obj["hop"])
                    self.clearedobjectives += 1
                    self.objectives.remove(obj)
                    target.flagout.remove(flag)
                    flag["capture"] = self.it
                    self.doneobjectives.append(flag)

        # total flag bandwidth vs current (last n steps)
        # Time vs steps
        self.flagbandwidth = len(self.doneobjectives)/self.it#flags/iteration
        # TODO visualize distribution
        # Include those not done?
        if len(self.doneobjectives) > 0:
            self.flagavglag = sum([flag["capture"]-flag["creation"] for flag in self.doneobjectives])/len(self.doneobjectives)

        #count false flags at the end

    def init(self):
        """Called after adding peers, initializes flags and time"""
        self.start = time()
        self.env()

    def run(self):
        self.init()
        #while time()<start+self.runtime:
        while self.it<100:
            self.update()

    def update(self):
        self.events = []
        # Peers may be moving
        self.connectivity = []
        simstart = time()
        index = Index((0,0,self.width,self.height))
        for peer in self.peers:#randomize order
            index.insert(peer.pid, (peer.pos[0],peer.pos[1],peer.pos[0]+1,peer.pos[1]+1))

        for peer in self.peers:
            peer.task.insert()
            stackless.run(1000)#run for n seconds?#randint(500,3000))
            peer.task.remove()
            self.csend += len(peer.sendarr)
            for pid in index.intersect((peer.pos[0]-self.radius,peer.pos[1]-self.radius,peer.pos[0]+1+self.radius,peer.pos[1]+1+self.radius)):
                peer2 = self.peers[pid]
                dist = wrappedDistance(peer.pos, peer2.pos, self.width, self.height)
                if peer2 != peer and dist<self.radius:#10/dist>random():
                    self.connectivity.append([peer, peer2, ""])
                    for msg in peer.sendarr:
                        #TODO package loss probability & distance loss
                        peer2.recv(msg)#aah, all packets sent at once! not realistic
                        self.events.append([peer, peer2, msg])
                        self.crecv += 1
            peer.sendarr = []
            #peer.pos = [(p+(random()-0.5)*0.2)%self.size for p in peer.pos]

        self.it += 1

        simend = time()
        if self.every:
            #os.system("clear")
            self.cbacklog = sum([len(peer.recvarr) for peer in self.peers])
            self.check()
            FlagAvgLag = self.flagavglag if self.flagavglag else float("NaN")
            InvFlagBandw = 1.0/self.flagbandwidth if self.flagbandwidth else float("NaN")
            roundresult = "ITER:{} FPS:{} Sent:{} Recv:{} Backlog:{} Flags:{} Cleared:{} FlAvgLag: {:.2f}it InvFlBw: {:.2f}it/fl".format(
                self.it, int(1/(simend-simstart)), self.csend, self.crecv, self.cbacklog, self.totalobjectives, self.clearedobjectives, FlagAvgLag, InvFlagBandw)
            print(roundresult)

            #self.draw()



    def draw(self):
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)
        for peer in self.peers:
            color = (0,0,255)
            if peer.pid == 0:
                color = (255,255,255)
            color = (min(255,len(peer.recvarr)),0,255)
            draw.rectangle(peer.pos+[peer.pos[0]+1,peer.pos[1]+1], color)
        img.save("anim/%i.png" % self.it)
