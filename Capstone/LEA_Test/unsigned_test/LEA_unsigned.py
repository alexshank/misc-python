'''
Alex Shank - 11/15/20

Script for analyzing the ADC samples of a microphone and
evaluating the results of the FFT computation completed by
the Low-Energy Accelerator of the MSP430.
'''
#from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
from util import * 

# MSP430 FFT results shown in debugger
mspResultsHex = getDebuggerValues()
result = []
for row in mspResultsHex:
    result.append(row[1])
mspResultsInt = hexVectorToIntVector(result)
mspResultsVoltage = intVectorToVoltageVector(mspResultsInt)
mspResultsVoltageReal = [mspResultsVoltage[i] for i in range(0, 512, 2)]
mspResultsVoltageImag = [mspResultsVoltage[i] for i in range(1, 513, 2)]
mspResultsVoltageMagnitude = fftMagnitudes(mspResultsVoltage)

# read in ADC data
adcInputsHexAndInt = []
with open('./Capstone/LEA_Test/unsigned_test/temp.txt') as f:
    for line in f:
        adcInputsHexAndInt.append(line[:-1])

# convert to decimal values
adcInputsInt = hexVectorToIntVector(adcInputsHexAndInt)

# convert input to voltage values
adcInputsVoltage = intVectorToVoltageVector(adcInputsInt)

# plot input voltage and python FFT result
Fs = 8192
N = 512
t = np.linspace(0, N * 1 / Fs, N, endpoint=False)
fig_1 = plt.figure(1)
plt.subplot(211)
plt.plot(t, adcInputsVoltage)
plt.title('Microphone ADC Samples (500 Hz Sin Wave)')
plt.xlabel('Time (sec)')
plt.ylabel('Voltage (V)')
plt.subplot(212)
[x, y] = getOneSidedFFT(adcInputsVoltage, N, Fs)
plt.plot(x, np.abs(y))
plt.title('FFT of ADC Samples (Python)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (V)')

# plot real and imag parts of MSP calculation
plt.figure(2)
plt.subplot(311)
plt.plot(x, mspResultsVoltageReal)
plt.title('MSP430 FFT Results')
plt.ylabel('Real (V)')
plt.xlabel('Frequency (Hz)')
plt.subplot(312)
plt.plot(x, mspResultsVoltageImag)
plt.ylabel('Imag (V)')
plt.xlabel('Frequency (Hz)')
plt.subplot(313)
plt.plot(x, mspResultsVoltageMagnitude)
plt.ylabel('Magnitude (V)')
plt.xlabel('Frequency (Hz)')

# plot real and imag parts of python calculation
plt.figure(3)
plt.subplot(311)
plt.plot(x, np.real(y))
plt.title('Python FFT Results')
plt.ylabel('Real (V)')
plt.xlabel('Frequency (Hz)')
plt.subplot(312)
plt.plot(x, np.imag(y))
plt.ylabel('Imag (V)')
plt.xlabel('Frequency (Hz)')
plt.subplot(313)
plt.plot(x, np.abs(y))
plt.ylabel('Magnitude (V)')
plt.xlabel('Frequency (Hz)')
plt.show()