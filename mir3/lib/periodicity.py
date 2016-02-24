#!/usr/bin/env python

# This program contains code regarding the paper:
# "Unsupervised training of detection threshold for polyphonic musical note tracking based on event periodicity"
# by Tiago Fernandes Tavares, Jayme G. A. Barbedo, Romis Attux and Amauri Lopes
# presented at the 38th International Conference on Acoustics, Speech, and Signal Processing (ICASSP),
# in Vancouver, British Columbia, Canada, May 2013.
# 
# Author's e-mail: tiagoft [at] gmail [dot] com
# Web page: http://www.dca.fee.unicamp.br/~tavares/
#
# Algorithm for use with automatic music transcription (please refer to paper for more details):
# 1) Calculate the activation matrix A[n][t] containing how active is note n at time frame t
# 2) We will calculate the best threshold to decide for active/inactive notes in A.
# 3) Select a range and a step for you threshold search
# 4) Apply threshold to activation matrix and calculate periodicity for each candidate
# 5) Accept threshold that yields the best periodicity
#
# See example below.

import numpy


def downsample(y,q=2):
    """Returns a downsampled version of y. Downsamples by a factor of q

    q must be an integer
    """
    x = numpy.zeros(int(len(y)/q))
    for n in xrange(len(x)):
        x[n]=numpy.max(y[n*q:(n+1)*q])
        #x[n]=y[n*q]
    return x

def hss(y, e=2.0, max_harmonics=8):
    """Calculates the harmonic sum spectrum of the input array y.

		Inputs:
		y - a 1-dimensional time-domain array
		e - use 1.0 for abs(fft), 2.0 for abs(fft)**2.0
		max_harmonics - the number of harmonics you want to use in this calculation.
    """
    Y = numpy.abs(numpy.fft.fft(  numpy.hanning(len(y))*(y-numpy.mean(y) )))**e
    s = numpy.sum(Y)

    maxhar = max_harmonics
    yd=[]
    for i in range(maxhar):
        yd.append(downsample(Y,i+1))
    kMax = len(yd[i])

    if s==0:
        return Y[0:kMax]
    #print Y
    hss = Y[0:kMax]
    #print hss
    for i in range(maxhar):
        hss = hss + yd[i][0:kMax]
        #print hss
    return hss/s

def periodicity(A, fs=44100.0/1024.0, min_freq=1.0/8.0, max_freq=8.0, e=2.0):
    """Returns the periodicity of an activation matrix A

    Algorithm:
    - Sum A over lines, getting array p[t]
    - Y[k] <- abs(fft(p[t]))
    - Return a measure of the periodicity (hps)

    Parameters:
    A - the activation matrix. Each channel is one line, each column is one time frame.
    fs - sampling frequency of A, in Hz.
    min_freq, max_freq - limits (in Hz) within the search for fundamental frequencies will be performed.
    e - will be used to calculate the hss.

    Returns:
    The periodicity measure (0 to 1)
    """
    y = numpy.sum(A,0)
    minK=len(y)*min_freq/fs
    maxK=len(y)*max_freq/fs

    h = hss(y, e=e)
    return numpy.max(h[minK:maxK])
