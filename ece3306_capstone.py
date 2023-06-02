from multiprocessing import Pool
import sys
import cmath as cm
import wave
import struct
import math
import time as tm
import numpy as np

def main():
    st = tm.time()
    #get raw data from the wav file
    data, rate, totalFrames = get_wave_data("sample.wav")
    threads = 6 #set the number of threads we're using
    processPool = Pool(processes=threads) #set the pool for multiprocessing
    channel_data_1 = list() #channel 1 data
    for i in data:
        channel_data_1.append(i[0]) #append only channel 1 data
    sections = list() #list for the data split up into sections
    time = int(totalFrames / rate) #total time of the file
    for i in range(time): #split up data into sections of each second (sections of 44100, the sampling rate)
        sections.append(channel_data_1[(i * rate):((i + 1) * rate)])
    final_data = processPool.map(decode, sections) #set up a variable to hold output data
    print("done", final_data) 
    print()
    print("Secret Secret Message: ","".join(final_data)) #print secret message
    end = tm.time()
    print()
    print("Run Time:", end-st)

def decode(section):
    n = len(section) #length of the input
    fhat = myfft(section) #perform the fft
    #filtering based on the index, 100,200,300,400,500,600,700,800 , are all frequencies we want the rest 
    #get turned into 0's
    for i in range(len(fhat)):
        if ((i == 100) or (i == 200)
                or (i == 300) or (i == 400)
                or (i == 500) or (i == 600)
                or (i == 700) or (i == 800)):
            fhat[i] = fhat[i]
        else:
            fhat[i] = 0
    return_value = list() #create a new list to hold the return value
    for i in range(1, 9): #ranging through the deseried frequencies * 10^-2
        #index mulitplied by 100 for the freq since we only want intervals of 100
        if (fhat[i * 100].real > .6e10): #threshold value of 0.6e10 signifies a 1 or 0 for binary
            if (i == 1): #if its the 100 freq, ignore the parity bit and change it to a zero
                return_value.append(0)
            else: #change to 1 since its greater than the threshold
                return_value.append(1)
        else: #not greater than threshold so change to 0
            return_value.append(0)
    string = [str(i) for i in return_value] #join the numbers together into a string
    string = "".join(string)
    return chr(int(string, 2)) #return the string converted into an int and then into a char


def myfft(signal):
  # Pad the signal with zeros to the next power of 2
  N = len(signal)
  M = 1
  while M < N:
    M *= 2

  # Compute the auxiliary sequence
  aux = [np.exp(-2j * np.pi * k * k / N) for k in range(N)]
  aux_fft = myfft(aux)

  # Compute the FFT of the padded signal
  padded_signal = signal + [0] * (M - N)
  padded_fft = myfft(padded_signal)

  # Compute the FFT of the original signal using Bluestein's algorithm
  return [aux_fft[k] * padded_fft[k] / aux_fft[0] for k in range(N)]


def fft(data):
    n = len(data) #get length of the input
    if n == 0: 
        return []
    elif n & (n - 1) == 0: #is a power of 2
        return power2(data)
    else: #not a power of 2 use a bluestein
        return bluestein(data)


def power2(data):
    n = len(data) #get length of input
    powerOf = n.bit_length() - 1 #find power of the length
    if 2 ** powerOf != n:
        raise ValueError("Not a power of two")
    #is a power of two
    w = -2 * cm.pi / n #the omega
    exp = [cm.rect(1, i * w) for i in range(n // 2)] #list of the exp in rectangular form
    data = [data[reverse(i, powerOf)] for i in range(n)] #copy with a bit reverse

    size = 2 #power 2 decimation, basically the cooley tukey algo
    while size <= n:
        halfsize = size // 2
        step = n // size
        for i in range(0, n, size): #ranging through size of the data with step increases
            f = 0
            for j in range(i, i + halfsize): #append in the new data times exp
                temp = data[j + halfsize] * exp[f]
                data[j + halfsize] = data[j] - temp
                data[j] += temp
                f = step + f
        size = size * 2 #increase the size
    return data


def bluestein(data):
    n = len(data)
    if n == 0:
        return []
    #finding a power of two to where it is bigger than n*2+1
    m = 2 ** ((n * 2).bit_length())
    #omega value
    w = -1 * cm.pi / n
    exp = [cm.rect(1, (i * i % (n * 2)) * w) for i in range(n)] #using trig for exp in rectangular form
    adata = [(x * y) for (x, y) in zip(data, exp)] + [0] * (m - n) #setting up the first list for convolution
    bdata = exp[:n] + [0] * (m - (n * 2 - 1)) + exp[:0:-1] #second list for convolution
    bdata = [i.conjugate() for i in bdata] #taking the conjugate of the second list to get rid of imaginary
    cdata = convolve(adata, bdata)[:n] #convolve the data and index it at the length of the original length of data
    return [(x * y) for (x, y) in zip(cdata, exp)] #return values with the exp multiplied


def convolve(a, b):
    n = len(a) #get the length of the input
    a = fft(a) #perform ffts on both again
    b = fft(b)
    for i in range(n): #multiply them to each other to get rid of imaginary
        a[i] *= b[i]
    a = fft(a) #take the fft again

    return [(x / n) for x in a] #return the new fft data divided by the length


def reverse(v, w): 
    #reverses the bits of w and returns the integer value 
    val = 0 
    for _ in range(w):
        val = (val << 1) | (v & 1)
        v >>= 1
    return val




def get_wave_data(file):
    #opens wave file as read only
    with wave.open(file, "rb") as wav:
        #using function to get the data we need from the wav file
        #finding channels, sampling width, framerate and number of frames
        nchannels, sampwidth, framerate, nframes, _, _ = wav.getparams()
        #checking if its big endian or little endian
        signed = sampwidth > 1
        order = sys.byteorder
        data = list() #new list for holding all the data converted
        for f in range(nframes): #going frame by frame
            frame = wav.readframes(1) #reading the frame and storing the value
            channels_data = list() #only useful for multiple channels
            for channel in range(nchannels): #ranging through the channel
                as_byte = frame[channel * sampwidth:(channel + 1) * sampwidth] #getting data 
                as_int = int.from_bytes(as_byte, order, signed=signed) #converting the data to an int
                channels_data.append(as_int) #appending to channel data list
            data.append(channels_data) #appending data into main data list
        return data, framerate, nframes #return framerate, number of frames, and data in int form


if __name__ == '__main__':
    main()