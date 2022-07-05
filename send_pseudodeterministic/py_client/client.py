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
import matplotlib.pyplot as plt
import numpy as np
from ctypes import *


""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("id", c_uint),
                ("input_0", c_float),
                ("input_1", c_float),
                ("input_2", c_float),
                ("input_3", c_float),
                ("fast1", c_float)]


def main():
    # WLAN: 192.168.1.3 for this RP
    # wired: 10.42.0.72 or see RP in Browser
    # port 2300 is random, ports over 1000 are usually not reserved
    server_addr = ('10.42.0.72', 2300)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bytecount = 0
    packagecount = 0
    errorcount = 0
    i = 0
    j = 0

    sample_time = 1000; # sample time in ns, fs = 1/sample time
    # this time needs to be increased if a deterministic error occurs
    # because this means that the sampling or plotting is too slow

    # turn on interactive mode for plot updating
    plt.ion()

    # prepare lists for buffers and plotting
    plot_buffer_size = 20000                    # size of the plotted data in one frame
    plot_length = 100                           # how many times the values are read
    plotdata0 = [0.0] * plot_buffer_size        # generate data list for plot
    data_buffer_size = 200                      # number of samples which are acquired before each plot update
    data_buffer_0 = [0.0] * data_buffer_size    # generate data buffer list

    # plot data for first time, filled with zeros
    x = list(range(0, plot_buffer_size))
    y = plotdata0
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(x, y, 'b-')

    time.sleep(1)


    try:
        s.connect(server_addr)
        print("Connected to {:s}".format(repr(server_addr)))
        connect_start = time.time()

        while j < plot_length:
            sample_start = time.time()
            while i < data_buffer_size:

                buff = s.recv(sizeof(Payload))
                try:
                    payload_in = Payload.from_buffer_copy(buff) # get data of payload
                    bytecount = bytecount + sizeof(Payload) # add up the total bytes sent
                    packagecount = packagecount + 1 # count packages sent
                    # data_buffer_0[i] = payload_in.fast1
                    data0[i] = payload_in.input_0 # store value of payload in0 in data0 list
                    data1[i] = payload_in.input_1
                    data2[i] = payload_in.input_2
                    data3[i] = payload_in.input_3
                except ValueError as ve:
                    errorcount = errorcount + 1
                    print("Package error")
                i = packagecount + errorcount
                time.sleep(0.001)
            sample_end = time.time_()
            # print("Sample time: ", sample_end - sample_start, "s")
            plot_start = time.time()
            # print("before update")

            # append the acquired data to the plotbuffer
            # first remove the length of the data at the beginning of the plotbuffer
            # so the plotbuffer stays the same size
            plotdata0 = plotdata0[data_buffer_size:plot_buffer_size]
            plotdata0.extend(data_buffer_0)

            # update the plot
            line1.set_ydata(plotdata0)
            fig.canvas.draw()
            fig.canvas.flush_events()
            plot_end = time.time()

            #print("Update time: ", plot_end-plot_start, "s")
            #print("Sample time: ", sample_end-sample_start, "s")

            # update loop variables
            j = j + 1
            i = 0
            packagecount = 0
            errorcount = 0



    except AttributeError as ae:
        print("Error creating the socket: {}".format(ae))
    except socket.error as se:
        print("Exception on socket: {}".format(se))
    finally:
        #print("i=", i)
        connect_end = time.time()
        elapsed = connect_end - connect_start
        print("Time for", bytecount, "Byte: ", elapsed,"s, Speed:", (bytecount/elapsed)/1000, "kB/s" )
        print(((bytecount/elapsed)/1000) / sizeof(Payload), "kilosamples per second")
        print("Errorcount: ", errorcount)
        print("Closing socket")
        s.close()


if __name__ == "__main__":
    main()
