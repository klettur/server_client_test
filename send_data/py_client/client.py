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
    _fields_ = [("id", c_uint),
                ("input_0", c_float),
                ("input_1", c_float),
                ("input_2", c_float)
                ("input_2", c_float)]


def main():
    server_addr = ('192.168.1.3', 2300)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bytecount = 0
    errorcount = 0

    try:
        s.connect(server_addr)
        print("Connected to {:s}".format(repr(server_addr)))
        i = 0
        start = time.time()
        while i < 1000:
            buff = s.recv(sizeof(Payload))
            #print("test1")

            try:
            #print("test2")
                payload_in = Payload.from_buffer_copy(buff)
                bytecount = bytecount + sizeof(Payload)
                # print("Value: {:f},".format(payload_in.data2))
            except ValueError as ve:
                errorcount = errorcount + 1
            #print("Received D1={:d}, D2={:d}, D3={:d}, D4={:d},".format(payload_in.data1,
                                                               #payload_in.data2,
                                                               #payload_in.data3,
                                                               #payload_in.data4))
            i = payload_in.data1
            #print(i)

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
        print("Time for ", bytecount, " Byte: ", elapsed)
        print("Errorcount: ", errorcount)
        print("Closing socket")
        s.close()


if __name__ == "__main__":
    main()
