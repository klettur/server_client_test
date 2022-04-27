#!/usr/bin/env python3

""" client.py - Echo client for sending/receiving C-like structs via socket
References:
- Ctypes: https://docs.python.org/3/library/ctypes.html
- Sockets: https://docs.python.org/3/library/socket.html
"""

import socket
import sys
import random
import time
from ctypes import *


""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("data1", c_uint32),
                ("data2", c_uint32),
                ("data3", c_uint32),
                ("data4", c_uint32)]


def main():
    server_addr = ('localhost', 2300)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect(server_addr)
        print("Connected to {:s}".format(repr(server_addr)))

        i = 0
        start = time.time()
        while i <= 1000:
            buff = s.recv(sizeof(Payload))
            payload_in = Payload.from_buffer_copy(buff)
            #print("Received D1={:d}, D2={:d}, D3={:d}, D4={:d},".format(payload_in.data1,
                                                               #payload_in.data2,
                                                               #payload_in.data3,
                                                               #payload_in.data4))
            i = payload_in.data1

        '''
        for i in range(5):
            print("")
            payload_out = Payload(1, i, random.uniform(-10, 30))
            print("Sending id={:d}, counter={:d}, temp={:f}".format(payload_out.id,
                                                              payload_out.counter,
                                                              payload_out.temp))
            nsent = s.send(payload_out)
            # Alternative: s.sendall(...): coontinues to send data until either
            # all data has been sent or an error occurs. No return value.
            print("Sent {:d} bytes".format(nsent))

            buff = s.recv(sizeof(Payload))
            payload_in = Payload.from_buffer_copy(buff)
            print("Received id={:d}, counter={:d}, temp={:f}".format(payload_in.id,
                                                               payload_in.counter,
                                                               payload_in.temp))
        '''
    except AttributeError as ae:
        print("Error creating the socket: {}".format(ae))
    except socket.error as se:
        print("Exception on socket: {}".format(se))
    finally:
        end = time.time()
        elapsed = end-start
        print("Time for 1000 16 Byte packages: ")
        print(elapsed)
        print("Closing socket")
        s.close()


if __name__ == "__main__":
    main()
