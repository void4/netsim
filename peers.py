from time import time
from random import random
from peer import Peer
from collections import Counter

# Tracks reliable neighbors
class TrackPeer(Peer):

    def setup(self):
        self.state["ping"] = {self.pid:{}}

    def track(self):
        rtime = time()

        if self.pingint:
            if len(self.recvarr)<5:
                self.send({"type":"ping", "origin":self.pid, "data":self.state["ping"][self.pid]})

        c = Counter()
        for msg in self.recvarr:
            c[msg["content"]["type"]] += 1

        if len(self.recvarr) > 0:
            msg = self.recvarr[0]

            target = msg["target"]
            source = msg["source"]
            content = msg["content"]

            if content["type"] == "ping":
                self.recvarr.pop(0)
                self.state["ping"][content["origin"]] = content["data"]

            if source != self.pid:
                if source not in self.state["ping"][self.pid]:
                    #self.p("found", source)
                    self.state["ping"][self.pid][source] = {"first":rtime,"last":rtime,"num":1}
                else:
                    self.state["ping"][self.pid][source]["last"] = rtime
                    self.state["ping"][self.pid][source]["num"] += 1

        for peer in list(self.state["ping"][self.pid]):
            if rtime-self.state["ping"][self.pid][peer]["last"]>5:
                #self.p("lost", peer)
                del self.state["ping"][self.pid][peer]

        if self.statint:
            #self.p("Peers:{} Knows:{}".format(len(self.state["ping"][self.pid]), len(self.state["ping"])-1))
            #self.p(self.state["ping"])
            pass


class GraphPeer(TrackPeer):

    def setup(self):
        super(GraphPeer, self).setup()
        self.pingint.interval = 2+random()


    # Finds a route, not necessarily the best
    def route(self, target, node=None, path=[], visited=[]):
        if node is None:
            node = self.pid

        if node == target:
            return [target]

        if not node in self.state["ping"]:
            return

        visited = list(visited)+[node]

        for peer in list(self.state["ping"][node]):

            if peer in visited:
                return
            result = self.route(target, peer, path, visited)
            if result:
                return [node]+result

    def update(self):

        if len(self.flagin)>0:
            flag = self.flagin.pop(0)
            if flag["target"] == self.pid:
                self.flagout.append(flag["content"])
            else:
                self.recvarr.append({"target":flag["target"], "source":self.pid, "content":flag})


        self.track()

        if len(self.recvarr) > 10:
            self.recvarr = [msg for msg in self.recvarr if msg["content"]["type"]!="ping"]

        if len(self.recvarr)==0 or self.recvarr[0]["content"]["type"] == "ping":
            return

        #self.p(self.state)

        msg = self.recvarr.pop(0)
        retry = False
        target = msg["target"]
        source = msg["source"]
        content = msg["content"]

        if content["type"] == "flag" and content["target"] == self.pid:
            self.flagout.append(content["content"])
        else:
            if "target" in content:
                path = self.route(content["target"])
                if path:
                    #self.p("route", path, target, msg)
                    self.send(content, target=path[1])
                else:
                    retry = True
            else:
                self.send(content)

        if retry:
            self.recvarr.append(msg)

# Implements basic packet flooding mechanism, does not resend packets with same seq number
class FloodPeer(TrackPeer):

    def setup(self):
        super(FloodPeer, self).setup()
        self.state["seq"] = {}

    def update(self):
        self.track()

        if len(self.flagin)>0:
            flag = self.flagin.pop(0)
            if flag["target"] == self.pid:
                self.flagout.append(flag["content"])
            else:
                self.send(flag)

        if len(self.recvarr) > 0:
            msg = self.recvarr.pop(0)
            target = msg["target"]
            source = msg["source"]
            content = msg["content"]

            #if content["type"] != "ping":
            if content["target"] == self.pid:
                if target == self.pid:
                    print(content)#"RECEIVED TARGETED PACKET")
                self.flagout.append(content["content"])
            else:
                # Might not receive packets in order!
                """
                if self.state["seq"].get(source, -1) < seq:
                    self.state["seq"][source] = seq
                """
                # Should use bloom filter here
                if source not in self.state["seq"]:
                    self.state["seq"][source] = []
                if seq not in self.state["seq"][source]:
                    self.state["seq"][source].append(seq)
                    if content["target"] in self.state["ping"]:
                        self.send(content, target=content["target"])
                        self.p("TARGETED PACKET", content)
                    else:
                        self.send(content)
                        #self.p("UNTARGETED PACKET")
