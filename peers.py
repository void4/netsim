from time import time

from peer import Peer

# Tracks reliable neighbors
class TrackPeer(Peer):

    def setup(self):
        self.state["ping"] = {}

    def track(self):

        rtime = time()

        if len(self.recvarr) > 0:
            msg = self.recvarr[0]
            target = msg["target"]
            source = msg["source"]
            seq = msg["seq"]
            content = msg["content"]

            if not source in self.state["ping"]:
                self.p("found", source)
                self.state["ping"][source] = {"first":rtime,"last":rtime,"num":1}
            else:
                self.state["ping"][source]["last"] = rtime
                self.state["ping"][source]["num"] += 1

        for peer in list(self.state["ping"]):
            if rtime-self.state["ping"][peer]["last"]>5:
                self.p("lost", peer)
                del self.state["ping"][peer]

        if self.statint:
            self.p("Peers: "+str(len(self.state["ping"])))

# Implements basic packet flooding mechanism, does not resend packets with same seq number
class FloodPeer(Peer):

    def setup(self):
        self.state["seq"] = {}

    def update(self):

        if self.pingint:
            self.send("ping")

        if len(self.flagin)>0:
            flag = self.flagin.pop()
            if flag["target"] == self.pid:
                self.flagout.append(flag["content"])
            else:
                self.send(flag)

        if len(self.recvarr) > 0:
            msg = self.recvarr.pop()
            target = msg["target"]
            source = msg["source"]
            seq = msg["seq"]
            content = msg["content"]

            if content != "ping":
                if content["target"] == self.pid:
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
                        self.state["seq"][source].append(self.send(content))
