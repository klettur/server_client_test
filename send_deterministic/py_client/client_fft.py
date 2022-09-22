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
from scipy.fft import fft, fftfreq

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

    fft_once = 0

    sample_time = 0.001; # sample time in s, fs = 1/sample time 0.0001
    # this time needs to be increased if a deterministic error occurs
    # because this means that the sampling is too slow
    # this is only a pseudo-sample time since plotting is slower
    # it just slows down the sampling to a defined time

    # turn on interactive mode for plot updating
    # plt.ion()

    # prepare lists for buffers and plotting
    plot_buffer_size = 20000                    # size of the plotted data in one frame
    plot_length = 10000                           # how many times the values are read
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
    #plt.figure(1)
    #fig, ax = plt.subplots()
    #(ln,)=ax.plot(x, y, animated=True)
    #ax.set_adjustable('datalim')
    #plt.axis([0, plot_length*2, 0, 4])
   # plt.show(block=False)
    #plt.pause(0.1)
   # bg = fig.canvas.copy_from_bbox(fig.bbox)
   # ax.draw_artist(ln)
   # fig.canvas.blit(fig.bbox)

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


            sample_end = time.time_ns()

            #
            plot_start = time.time_ns()

            plotdata0 = plotdata0[data_buffer_size:plot_buffer_size]
            plotdata0.extend(data_buffer_0)


            if j == 300: # plotdata0[0] != 0 and fft_once == 0:
                N = 20000
                fs = 2000

                yf = fft(plotdata0)
                xf = fftfreq(N, 1 / fs)

                plt.plot(xf, np.abs(yf))
                print("before show")
                plt.show()
                print("fig 1 done")
#------------------------------------
                # iirnotch

                #f0 = 52.4
                ## fs = 1/sample_time
                ## fs = 2500
                #w0 = f0/(fs/2)
                #Q = 10
                #b, a = iirnotch(w0, Q)

                #filtered1 = filtfilt(b, a, plotdata0)

                ## another time with 100Hz for first harmonics

                #f0 = 104.8
                ## fs = 1/sample_time
                ## fs = 2500
                #w0 = f0/(fs/2)
                #Q = 10
                #b, a = iirnotch(w0, Q)

                #filtered = filtfilt(b, a, filtered1)

                #yf = fft(filtered)
                #xf = fftfreq(N, 1 / fs)
                #plt.plot(xf, np.abs(yf))
                #plt.show()
#-------------------------------------
                # iircomb
                f0 = 50
                # fs = 1/sample_time
                # fs = 2500
                w0 = f0/(fs/2)
                Q = 5
                b, a = iircomb(w0, Q)

                filtered = filtfilt(b, a, plotdata0)

                yf = fft(filtered)
                xf = fftfreq(N, 1 / fs)
                plt.plot(xf, np.abs(yf))
                plt.show()

#-----------------------------------------
                ## low pass
                #f0 = 50
                ## fs = 1/sample_time
                ## fs = 2500
                #fs = 2000
                #w0 = f0/(fs/2)
                #b,a = butter(10, 120/(fs/2))
                #filtered2 = filtfilt(b, a, filtered)
                #yf = fft(filtered1)
                #xf = fftfreq(N, 1 / fs)
                #plt.plot(xf, np.abs(yf))
                #plt.show()


                fft_once = 1
                #print("fft done")
                #time.sleep(20)
                # sampling rate
                #sr = 2000
                ## sampling interval
                #ts = 1.0/sr
                #t = np.arange(0,1,ts)

                #freq = 1.
                #x = 3*np.sin(2*np.pi*freq*t)

                #freq = 4
                #x += np.sin(2*np.pi*freq*t)

                #freq = 7
                #x += 0.5* np.sin(2*np.pi*freq*t)

                #plt.figure(figsize = (8, 6))
                #plt.plot(t, x, 'r')
                #plt.ylabel('Amplitude')

                #plt.show()

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
