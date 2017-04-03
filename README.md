# NetSim
should probably be called MeshSim. Works with Stackless Python.

```python3 main.py```

Simulates p2p nodes in a 2d wireless environment. Peers may receive flag messages that they must transmit to other specific nodes. Collaboration is necessary.
New Peers should subclass Peer and only specify two functions:

- `setup`: Called once at node creation, should be used to setup self.state
- `update`: Called as long as the node is alive, can send() packets and read from self.recvarr

All state should reside in the self.state dictionary so it can be easily analysed.

#### Output example:

`ITER:39 FPS:6 Sent:269389 Recv:449557 Backlog:178771 Flags:500 Cleared:80`
