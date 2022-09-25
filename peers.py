from time import time
from random import random
from collections import Counter

from peer import Peer
from utils import Every

# Tracks reliable neighbors
class TrackPeer(Peer):

    def setup(self):
        self.state["ping"] = {self.pid:{}}
        self.timeout = None#5
        self.pingint = Every(30, randomoffset=30)#TODO add random start timeshift

    def get_knownpeers(self):
        return set(list(self.state["ping"].keys())) | set([pid for kv in list(self.state["ping"].values()) for pid in list(kv.keys())])

    def track(self):
        # TODO: avoid mutual sends?
        rtime = time()

        if self.pingint:
            #if len(self.recvarr)<5:
            self.send({"type":"ping", "origin":self.pid, "data":self.state["ping"]})#[self.pid]

        c = Counter()
        for msg in self.recvarr:
            c[msg["content"]["type"]] += 1

        if len(self.recvarr) > 0:
            msg = self.recvarr[0]

            target = msg["target"]
            source = msg["source"]
            content = msg["content"]

            if content["type"] == "ping" and content["origin"] != self.pid:
                self.recvarr.pop(0)

                #self.state["ping"][content["origin"]] = content["data"]
                updates = 0
                stale = 0
                # TODO with moving/disconnecting peers, consider timeout even of those not sent
                for key1, value1 in list(content["data"].items()):
                    for key2, value2 in list(value1.items()):
                        #print(key1, key2, value2)
                        if key1 not in self.state["ping"]:
                            self.state["ping"][key1] = {}

                        if key2 not in self.state["ping"][key1]:
                            self.state["ping"][key1][key2] = value2
                            updates += 1
                        else:
                            if value2["num"] > self.state["ping"][key1][key2]["num"]:
                                self.state["ping"][key1][key2] = value2
                                updates += 1
                            else:
                                stale += 1
                #print("u:", updates, "s:", stale)
                #this should inversely depend on range to eventual receiving node/sending node? every node should have the same chance
                # local node info shouldn't saturate the local net
                # check how many unknowns there are, perhaps good proxy

                """
                knownpeers = self.get_knownpeers()
                gossippeers = set(content["data"].keys()) | set([content["origin"]])
                #print(gossippeers, knownpeers)
                numunknowns = len(gossippeers.difference(knownpeers))
                if numunknowns > 0:
                    print("unknowns:", numunknowns)
                """

                # ocassionally sent unknown deltas only?
                #if len(self.recvarr)<100 and ((numunknowns > 0 and random() < 1) or random()<0.05):#adjust probabilities with number of own peers, or "density" of locality
                #    self.send(msg["content"])

            # TODO: send occassional updates to the *edge* of the known network

            # This tracks all direct contacts, not just ping packets
            if source != self.pid:
                if source not in self.state["ping"][self.pid]:
                    #self.p("found", source)
                    self.state["ping"][self.pid][source] = {"first":rtime,"last":rtime,"num":1}
                else:
                    self.state["ping"][self.pid][source]["last"] = rtime
                    self.state["ping"][self.pid][source]["num"] += 1

        if self.timeout:
            for peer in list(self.state["ping"][self.pid]):
                if rtime-self.state["ping"][self.pid][peer]["last"] > self.timeout:
                    #self.p("lost", peer)
                    del self.state["ping"][self.pid][peer]

        if self.statint:
            #self.p("Peers:{} Knows:{}".format(len(self.state["ping"][self.pid]), len(self.state["ping"])-1))
            #self.p(self.state["ping"])
            pass

    def update(self):
        self.track()


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
                self.flagout.append(flag)
            else:
                self.recvarr.append({"target":flag["target"], "source":self.pid, "content":flag})


        self.track()

        #if len(self.recvarr) > 10:
        #    self.recvarr = [msg for i, msg in enumerate(self.recvarr) if msg["content"]["type"]!="ping" or i<10]

        if len(self.recvarr)==0 or self.recvarr[0]["content"]["type"] == "ping":
            return

        #self.p(self.state)

        msg = self.recvarr.pop(0)
        retry = False
        target = msg["target"]
        source = msg["source"]
        content = msg["content"]

        if content["type"] == "flag" and content["target"] == self.pid:
            self.flagout.append(content)
        else:
            if "target" in content:
                path = self.route(content["target"])
                if path:
                    #self.p("route", path, target, msg)
                    if "hop" in content:
                        content["hop"] += 1
                    self.send(content, target=path[1])
                else:
                    retry = True
            else:
                self.send(content)

        if retry:
            self.recvarr.append(msg)

class EmptyPeer(Peer):
    def setup(self):
        pass

    def update(self):
        self.p(self.recvarr)
        self.recvarr = []
        self.send("test")

# Implements basic packet flooding mechanism, does not resend packets with same seq number
class FloodPeer(TrackPeer):

    def setup(self):
        super(FloodPeer, self).setup()
        self.state["seq"] = {}

    def update(self):
        #self.track()

        if len(self.flagin)>0:
            flag = self.flagin.pop(0)
            if flag["target"] == self.pid:
                self.flagout.append(flag)
            else:
                self.send(flag)

        if len(self.recvarr) > 0:
            msg = self.recvarr.pop(0)
            target = msg["target"]
            source = msg["source"]
            content = msg["content"]

            #if content["type"] != "ping":
            if content.get("target") == self.pid:
                #if target == self.pid:
                #    print(content)#"RECEIVED TARGETED PACKET")
                self.flagout.append(content)
            elif "seq" in msg:
                #print(msg)
                seq = msg["seq"]
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
                    if content.get("target") in self.state["ping"]:
                        self.send(content, target=content["target"], seq=msg["seq"])
                        #self.p("TARGETED PACKET", content)
                    else:
                        self.send(content, seq=msg["seq"])
                        #self.p("UNTARGETED PACKET")

# TODO BloomFilterGossip
