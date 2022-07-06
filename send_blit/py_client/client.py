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
import matplotlib
matplotlib.use('GTK3Agg') # was GTKAgg, nbAgg also not working
import numpy as np
from matplotlib import pyplot as plt
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

    sample_time = 0.0001; # sample time in s, fs = 1/sample time 0.0001
    # this time needs to be increased if a deterministic error occurs
    # because this means that the sampling or plotting is too slow

    # turn on interactive mode for plot updating
    plt.ion()

    # prepare lists for buffers and plotting
    plot_buffer_size = 20000                    # size of the plotted data in one frame
    plot_length = 200                           # how many times the values are read
    plotdata0 = [0.0] * plot_buffer_size        # generate data list for plot
    data_buffer_size = 200                      # number of samples which are acquired before each plot update
    data_buffer_0 = [0.0] * data_buffer_size    # generate data buffer list

    # plot data for first time, filled with zeros
    x = list(range(0, plot_buffer_size))
    # print("xlen: ", len(x))

    y = plotdata0
    # print("ylen: ", len(y))

    # fig, ax = plt.subplots(1, 1)

    fig, ax = plt.subplots()
    (ln,)=ax.plot(x, y, animated=True)
    plt.show(block=False)
    plt.pause(0.1)
    bg = fig.canvas.copy_from_bbox(fig.bbox)
    ax.draw_artist(ln)
    fig.canvas.blit(fig.bbox)
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # line1, = ax.plot(x, y, 'b-')
    # points = ax.plot(x,y, 'o')[0]

    time.sleep(1)

    printcount = 1
    errorcount_all = 0
    printtime = 0
    connect_start = 0
    connect_end = 0


    try:
        s.connect(server_addr)
        print("Connected to {:s}".format(repr(server_addr)))
        connect_start = time.time()

        while j < plot_length:
            sample_start = time.time_ns()
            while i < data_buffer_size:

                buff = s.recv(sizeof(Payload))
                try:
                    sample_start_time = time.time_ns()
                    payload_in = Payload.from_buffer_copy(buff) # get data of payload
                    bytecount = bytecount + sizeof(Payload) # add up the total bytes sent
                    packagecount = packagecount + 1 # count packages sent
                    data_buffer_0[i] = payload_in.input_0
                    # data0[i] = payload_in.input_0 # store value of payload in0 in data0 list
                    # data1[i] = payload_in.input_1
                    # data2[i] = payload_in.input_2
                    # data3[i] = payload_in.input_3

                    if (time.time_ns() - sample_start_time) >= 0:
                        time.sleep(sample_time - ((time.time_ns() - sample_start_time) / 1000000000))
                    else:
                        print("Deterministic error, sampling too slow")

                except ValueError as ve:
                    errorcount = errorcount + 1
                    errorcount_all = errorcount_all + 1
                    print("Package error")
                i = packagecount + errorcount
                # time.sleep(0.001)
            sample_end = time.time_ns()

            #if j == 1:
              #  fig, ax = plt.subplots()
               # (ln,)=ax.plot(x, y, animated=True)
               # plt.show(block=False)
              #  plt.pause(0.1)
              #  bg = fig.canvas.copy_from_bbox(fig.bbox)
              #  ax.draw_artist(ln)
             #   fig.canvas.blit(fig.bbox)

            # print("Sample time: ", sample_end - sample_start, "s")
            plot_start = time.time_ns()
            # print("before update")

            # append the acquired data to the plotbuffer
            # first remove the length of the data at the beginning of the plotbuffer
            # so the plotbuffer stays the same size
            plotdata0 = plotdata0[data_buffer_size:plot_buffer_size]
            plotdata0.extend(data_buffer_0)

            # print("plotdata0 len: ", len(plotdata0))

            # update the plot
            fig.canvas.restore_region(bg)
            ln.set_ydata(plotdata0)

            ax.draw_artist(ln)
            fig.canvas.blit(fig.bbox)
            fig.canvas.flush_events()

            # line1.set_ydata(plotdata0)
            # fig.canvas.draw()
            # fig.canvas.flush_events()
            plot_end = time.time_ns()

            printcount = printcount + 1
            printtime = printtime + (plot_end - plot_start)

            # print("Update time: ", plot_end-plot_start/1000000, "ms")
            # print("Sample time: ", sample_end-sample_start/1000000, "ms")

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
        avgtime = (printtime/printcount)/1000000
        print("Average plot update time: ", avgtime, "ms")
        connect_end = time.time()
        elapsed = connect_end - connect_start
        print("Time for", bytecount, "Byte: ", elapsed,"s, Speed:", (bytecount/elapsed)/1000, "kB/s" )
        print(((bytecount/elapsed)/1000) / sizeof(Payload), "kilosamples per second")
        print("Errorcount: ", errorcount_all)
        print("Closing socket")
        s.close()


if __name__ == "__main__":
    main()
