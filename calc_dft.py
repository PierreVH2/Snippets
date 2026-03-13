#!/usr/bin/python2

import math
import numpy

def calc_dft_deeming (data, startfreq, stopfreq, freqstep):
  """
  Function to calculate the Fourier transform of unequally spaced data, based on the algorithm by Deeming
  (see 'Fourier analysis with unequally-spaced data' T.J. Deeming, ApSS 36, 1975, 137-158 and
  'An Algorithm for significantly reducing the time necessary to compute a Discrete Fourier Transform
  periodogram of unequally space data' D.W. Kurtz, MNRAS 213, 1985, 773-776).
  
  
  'data' - Input data, must be a shape (2,N) numeric array, where N is the number of data points.
  The independent variable (probably time) values must be in [0,:] and can have any unit
  The dependent variable (probably magnitude) values must be in [1,:] and can have any unit
  
  'startfreq' - The first frequency at which the FT must be calculated
  Unit is the inverse of the unit of time used in 'data'
  
  'stopfreq' - The last frequency at which the FT must be calculated
  Unit is the inverse of the unit of time used in 'data'
  
  'freqstep' - The spacing between consecutive frequencies at which the FT must be calculated
  Unit is the inverse of the unit of time used in 'data'
  
  Returns a shape (2,K) numeric array, where K is the number of frequencies where the FT was calculated
  The frequencies are stored in [0,:] and have the inverse unit as that of the independent variable.
  The Fourier transforms are stored in [0,:] and have the same unit as that of the dependent variable.
  """
  
  # Extract timestamps and subtract epoch
  t = numpy.matrix(data[0])
  t -= math.floor(t.min())
  # Extract magnitudes and subtract mean
  f = numpy.matrix(data[1])
  f -= f.mean()
  # Set up vector of frequencies at which Fourier transform must be calculated
  freqs = numpy.matrix(numpy.arange(startfreq,stopfreq,freqstep))
  # Create matrix 'a', containing each unique combination of time and frequency
  a = 2*math.pi*t.transpose()*freqs
  # Calculate the real and imaginary parts of the DFT
  dftR = f * numpy.cos(a)
  dftI = f * numpy.sin(a)
  # Calculate the DFT, combine with the vector of frequencies and return the result.
  FF = 2 * (numpy.array(dftR)**2 + numpy.array(dftI)**2)**0.5 / (f.shape[1])
  freqs /= 86.4
  FF *= 1000.0
  return numpy.append(freqs,FF,axis=0)
