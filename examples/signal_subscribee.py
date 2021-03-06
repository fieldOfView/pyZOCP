#!/usr/bin/python3

from zocp import ZOCP
import socket
import logging
from threading import Event, Thread

class SubscribableNode(ZOCP):
    # Constructor
    def __init__(self, nodename=""):
        self.nodename = nodename
        self.float_value = 1.0
        self.count_value = 0
        self.counter_active = False
        self.string_value = ''
        super(SubscribableNode, self).__init__()


    def run(self):
        self.set_name(self.nodename)
        self.register_float("My Float", self.float_value, 'rwe')
        self.register_bool("Counter active", self.counter_active, 'rw')
        self.register_float("Counter", self.count_value, 're')
        self.register_string("My String", self.string_value, 'rwe')
        self.start()

        self.stop_timer = self.call_repeatedly(1, self.on_timer)
        super(SubscribableNode, self).run()

    
    def stop(self):
        self.stop_timer()
        super(SubscribableNode, self).stop()


    def on_modified(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            for key in data:
                if 'value' in data[key]:
                    self.receive_value(key)

                
    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            for sensor in data[2]:
                if(sensor):
                    self.receive_value(sensor)


    def receive_value(self, key):
        new_value = self.capability[key]['value']

        if key == "My Float":
            if new_value != self.float_value:
                self.float_value = new_value
        if key == "My String":
            if new_value != self.string_value:
                self.string_value = new_value
        if key == "Counter active":
            if new_value != self.counter_active:
                self.counter_active = new_value


    def on_timer(self, *args):
        if self.counter_active:
            self.count_value += 1
            self.emit_signal('Counter', self.count_value)


    def call_repeatedly(self, interval, func, *args):
        stopped = Event()
        def loop():
            while not stopped.wait(interval): # the first call is in `interval` secs
                func(*args)
        Thread(target=loop).start()
        return stopped.set
    
        
if __name__ == '__main__':
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.DEBUG)

    z = SubscribableNode("subscribee@%s" % socket.gethostname())
    z.run()
    print("FINISH")
