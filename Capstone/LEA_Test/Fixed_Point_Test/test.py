'''
Alex Shank - 11/11/20

'''
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from fxpmath import Fxp
import math

# get FFT of passed in signal
def getFFT(samples):
    N = len(samples)
    return np.abs(np.fft.fft(samples, N)/ (N / 2))      # ignore phase

# plot one sided FFT of passed in signal
def plotFFT(samples, samples2):
    N = len(samples)
    y_fft = np.abs(np.fft.fft(samples, N)) / (N / 2)     # ignore phase
    y_fft_2 = np.abs(np.fft.fft(samples2, N)) / (N / 2)     # ignore phase
    plt.plot(y_fft)
    plt.plot(y_fft_2)


# convert from decimal to fixed point representation
def convertToIq(num):
    return Fxp(num, signed=True, n_word=16, n_frac=15)

# compute signed int from given hex value
# (deprecated: unsigned ints now being used)
def twos_complement(hexstr,bits=16):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value


# convert from decimal to fixed point representation
def convertToDecimal(n):
    signed_n = twos_complement(hex(n))
    return signed_n*(2**-15)

def vectorMagnitudes(samples):
    result = []
    for i in range(int(len(samples) / 2)):
        result.append(math.sqrt(samples[i]**2 + samples[i+1]**2))
    return result


# create data
originalDecimals = [i * 0.002 for i in range(16)]
fftInputs = [0x0000, 0x0041, 0x0083, 0xC4, 0x106, 0x147, 0x189, 0x1CA, 0x20C, 0x24D, 0x28F, 0x2D0, 0x312, 0x353, 0x395, 0x3D7]
fftOutputs = [0x3CC, 0x0000, 0xFFBD, 0x149, 0xFFBE, 0x9C, 0xFFBD, 0x61, 0xFFC0, 0x42, 0xFFC1, 0x2D, 0xFFC0, 0x001A, 0xFFBF, 0xD]
decFFT = getFFT(originalDecimals)


# write CSV data to output file
inputConvertedDecimal = []
outputConvertedDecimal = []
f = open("./Capstone/LEA_Test/output.csv", "w")
f.write('dec, q15in (py), q15in (msp), q15inDec (py), q15out (msp), q15FFTdec (msp/py), decFFT (py), decFFTq15 (py)\n')
for i in range(16):
    # decimal input
    f.write(str(originalDecimals[i]) + ', ')

    # q15 representation of decimal input (my conversion)
    t = convertToIq(originalDecimals[i])
    f.write(t.hex() + ', ')

    # MSP430's q15 representation of input
    f.write(hex(fftInputs[i]) + ', ')

    # actual q15 output converted to decimal (msp/py)
    t5 = convertToDecimal(fftInputs[i])
    inputConvertedDecimal.append(t5)
    f.write(str(t5) + ', ')


    # MSP430's q15 representation of output
    f.write(hex(fftOutputs[i]) + ', ')

     # actual q15 output converted to decimal (msp/py)
    t4 = convertToDecimal(fftOutputs[i])
    outputConvertedDecimal.append(t4)
    f.write(str(t4) + ', ')

    # decimal output (mine)
    t2 = getFFT(originalDecimals)   # inefficient
    f.write(str(t2[i]) + ', ')

    # decimal output converted to q15 (mine)
    t3 = convertToIq(t2[i])
    f.write(t3.hex() + '\n')
f.close()

# plot input (decimal values) and FFT results
plt.figure(1)
plt.subplot(211)
plt.plot(originalDecimals)
plt.plot(inputConvertedDecimal)
plt.subplot(212)
plotFFT(originalDecimals, inputConvertedDecimal)

# plot decimal output (with calculated magnitude)
plt.figure(2)
N = len(inputConvertedDecimal)
y_fft = np.abs(np.fft.fft(inputConvertedDecimal, N)) / (N / 2)
plt.plot(y_fft[:round(N/2)])
plt.plot(vectorMagnitudes(outputConvertedDecimal))
'''
plt.figure(3)
N = len(inputConvertedDecimal)
plt.subplot(211)
plt.plot(np.real(np.fft.fft(inputConvertedDecimal, N)) / (N / 2))     # ignore phase
plt.plot(np.imag(np.fft.fft(inputConvertedDecimal, N)) / (N / 2))     # ignore phase
plt.subplot(212)
plt.plot(np.angle(np.fft.fft(inputConvertedDecimal, N)) / (N / 2))     # ignore phase
plt.plot(np.abs(np.fft.fft(inputConvertedDecimal, N)) / (N / 2))     # ignore phase
'''
plt.show()

# test input (500 Hz)
f = 500
fs = 2048 
N = 16
t = np.linspace(0, N * 1 / fs, N, endpoint=False)
signal = 0.2 * np.cos(2 * np.pi * f * t) + 0.250

NADC = np.round(4096 * (signal + 3.3 / 8192) / 3.3)
print(NADC)