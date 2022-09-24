import stackless
from utils import Every

# Add local time with different offset and speed
# Or number of executed instructions
class Peer:
    def __init__(self):
        # Unique Peer ID
        self.pid = None

        # Packet sequence number
        self.seq = 0

        # 2D-position of peer
        self.pos = [0,0]

        # Stackless tasklet
        self.task = stackless.tasklet(self.main)()

        # Receive and Send packet buffer
        self.recvarr = []
        self.sendarr = []

        # Statistics output interval
        self.pingint = Every(0.25)
        self.statint = Every(0.5)

        # Flag input and output
        self.flagin = []
        self.flagout = []

        # Peer state - only this should be accessed within update()
        self.state = {}

    # Main tasklet function
    def main(self):
        self.setup()
        while True:
            self.update()

    # Setting up self.state
    def setup(self):
        pass

    # Adds received packets to the receive buffer, discards them if they are not addressed
    # to either the peer or the broadcast address (None)
    def recv(self, msg):
        if msg["target"] in [None, self.pid]:
            self.recvarr.append(msg)

    # Constructs a packet and puts it in the outgoing buffer
    # By default, the packet is broadcast to all peers
    def send(self, msg, target=None, seq=None):
        if seq is None:
            seq = self.seq
            self.seq += 1
        self.sendarr.append({"target":target, "source":self.pid, "seq":seq, "content":msg})


    # This function is called as long as the peer is alive
    def update(self):
        pass

    # Facilitates debug output for peer 0
    def p(self, *args):
        if self.pid == 0:
            print(self.pid, str(args))
