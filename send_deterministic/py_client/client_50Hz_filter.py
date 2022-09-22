#!/usr/bin/env python3

"""
References Ctypes and Sockets:
- Ctypes: https://docs.python.org/3/library/ctypes.html
- Sockets: https://docs.python.org/3/library/socket.html
"""

import socket
import sys
import random
import time
import matplotlib
matplotlib.use('GTK3Agg')   # don't use conda for installing dependencies, it screws up the path
                            # only use pip
import numpy as np
from matplotlib import pyplot as plt
from ctypes import *

from scipy.signal import filtfilt, iirnotch, freqz, butter, iircomb
from scipy.fftpack import fft, fftshift, fftfreq

# This class defines a C-like struct
# used for getting the received payload from the c-server
class Payload(Structure):
    _fields_ = [("id", c_uint),
                ("input_0", c_float * 200),
                ("input_1", c_float),
                ("input_2", c_float),
                ("input_3", c_float),
                ("fast1", c_float)]


def main():
    # WLAN: 192.168.1.3 for this RP
    # wired: 10.42.0.72 or see RP in Browser
    # port 2300 is random, ports over 1000 are usually not reserved
    # just needs to be the same port as on the server
    server_addr = ('10.42.0.72', 2300)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # initialize various count variables
    bytecount = 0
    packagecount = 0
    errorcount = 0
    i = 0
    j = 0

    sample_time = 0.0001; # sample time in s, fs = 1/sample time 0.0001
    # this time needs to be increased if a deterministic error occurs
    # because this means that the sampling is too slow
    # this is only a pseudo-sample time since plotting is slower
    # it just slows down the sampling to a defined time

    # turn on interactive mode for plot updating
    plt.ion()

    # prepare lists for buffers and plotting
    plot_buffer_size = 20000                    # size of the plotted data in one frame
    plot_length = 10000                          # how many times the values are read
    plotdata0 = [0.0] * plot_buffer_size        # generate data list for plot
    data_buffer_size = 200                      # number of samples which are acquired before each plot update
    data_buffer_0 = [0.0] * data_buffer_size    # generate data buffer list

    # generate x axis
    x = list(range(0, plot_buffer_size))
    # print("xlen: ", len(x)) # for checking length of x axis

    # assigning data (now emtpy) to y axis
    y = plotdata0
    # print("ylen: ", len(y)) # for checking length of y axis

    # create background and plot for the first time
    # see https://matplotlib.org/stable/tutorials/advanced/blitting.html
    # for more information
    fig, ax = plt.subplots()
    (ln,)=ax.plot(x, y, animated=True)
    plt.axis([0, plot_buffer_size*2, 0, 4])
    plt.show(block=False)
    plt.pause(0.1)
    bg = fig.canvas.copy_from_bbox(fig.bbox)
    ax.draw_artist(ln)
    fig.canvas.blit(fig.bbox)

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
            sample_start = time.time_ns

            buff = s.recv(sizeof(Payload))

            try:
                payload_in = Payload.from_buffer_copy(buff) # get data of payload
                bytecount = bytecount + sizeof(Payload) # add up the total bytes sent
                packagecount = packagecount + 1 # count packages sent
                data_buffer_0 = payload_in.input_0

            except ValueError as ve:
                errorcount = errorcount + 1
                errorcount_all = errorcount_all + 1
                print("Package error")

            #while i < data_buffer_size:

                #buff = s.recv(sizeof(Payload))
                #try:
                    #sample_start_time = time.time_ns()
                    #payload_in = Payload.from_buffer_copy(buff) # get data of payload
                    #bytecount = bytecount + sizeof(Payload) # add up the total bytes sent
                    #packagecount = packagecount + 1 # count packages sent
                    #data_buffer_0[i] = payload_in.input_0

                    # stupid filter
                    # if data_buffer_0[i] > 2.5 or data_buffer_0[i] < 0.3:
                    #     data_buffer_0[i] = 1.8

                    # data_buffer_1[i] = payload_in.input_1
                    # data_buffer_2[i] = payload_in.input_2
                    # data_buffer_3[i] = payload_in.input_3

                    # wait until sampling time is over
                    #if (sample_time*1000000000 - (time.time_ns() - sample_start_time)) >= 0:
                        #time.sleep(sample_time - ((time.time_ns() - sample_start_time) / 1000000000))
                    #else:
                        ## if sampling takes longer than sample time
                        #print("Deterministic error, sampling too slow")

                    # sample_end = time.time_ns()-sample_start_time
                    # print("Sample time: ", sample_end)

                #except ValueError as ve:
                    #errorcount = errorcount + 1
                    #errorcount_all = errorcount_all + 1
                    #print("Package error")
                #i = packagecount + errorcount
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
            # plotdata0.extend(data_buffer_0)
            plotdata0.extend(data_buffer_0)

            # filter test
            #N = 1000
            #fs = 2000

            ## iircomb
            #f0 = 50
            #fs = 2000
            ## fs = 1/sample_time
            ## fs = 2500
            #w0 = f0/(fs/2)
            #Q = 7
            #b, a = iircomb(w0, Q)

            #filtered = filtfilt(b, a, plotdata0)

            #yf = fft(plotdata0[0:1000])
            #xf = fftfreq(N, 1 / fs)

            #plt.plot(xf, np.abs(yf))
            #print("before show")
            #plt.show()
            #print("fig 1 done")
#------------------------------------
            # iirnotch

            f0 = 50
            # fs = 1/sample_time
            fs = 2000
            w0 = f0/(fs/2)
            Q = 5
            b, a = iirnotch(w0, Q)

            filtered1 = filtfilt(b, a, plotdata0)

            # another time with 100Hz for first harmonics

            f0 = 100
            # fs = 1/sample_time
            # fs = 2500
            w0 = f0/(fs/2)
            Q = 5
            b, a = iirnotch(w0, Q)

            filtered = filtfilt(b, a, filtered1)


            b,a = butter(10, 75/fs)

            filtered2 = filtfilt(b, a, filtered)

            # print("plotdata0 len: ", len(plotdata0))

            # update the plot
            fig.canvas.restore_region(bg)
            ln.set_ydata(filtered2)

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
