import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from fxpmath import Fxp
import math
from bs4 import BeautifulSoup

# some hex values already converted to decimal in CCS, so
# ignore previously converted values
def hexVectorToIntVector(vector):
    result = []
    for v in vector:
        if('x' in v):
            n = int(v[2:], 16)   # dec value of sample
        else:
            n = int(v)
        result.append(n)
    return result

# convert the ADC hex value into corresponding voltage
# formula found on page 871 of
# MSP430FR58xx, MSP430FR59xx, and MSP430FR6xx Family User's Guide (Rev. P)
def intVectorToVoltageVector(intVector):
    result = []
    for n in intVector:
        VR_Pos = 3.3
        VR_Neg = 0
        V_In = n / 4096 * (VR_Pos - VR_Neg)
        V_In = V_In + VR_Neg - (VR_Pos - VR_Neg) / 8192
        result.append(V_In)
    return result

# convert a given voltage to its ADC representation
def voltageVectorToIntVector(voltageVector):
    result = []
    for V_In in voltageVector:
        NADC = np.round(4096 * (V_In + 3.3 / 8192) / 3.3)
        result.append(NADC)
    return result

# get one sided FFT of passed in signal
def getOneSidedFFT(samples, N, Fs):
    x_fft = np.fft.fftfreq(N, d=1/Fs)           # bin frequencies
    #y_fft = np.abs(np.fft.fft(samples, N))      # ignore phase
    y_fft = np.fft.fft(samples, N)      # ignore phase
    y_fft = y_fft / (N / 2)                      # double energy because left side eliminated
    #y_fft = 20*np.log10(y_fft / max(y_fft))     # normalized dB magnitude
    return [x_fft[:round(N/2)], y_fft[:round(N/2)]]     # return only the right side


# MSP430 FFT results shown in debugger
def getDebuggerValues():
    # open the input file (that is manually copied from CCS Online)
    with open('./Capstone/LEA_Test/unsigned_test/input.html', 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, 'html.parser')

    # get div containing debugging values (output of MSP430 FFT)
    dataRows = []
    tableDiv = soup.findAll("div", class_="records")
    for rowDiv in tableDiv:
        row = rowDiv.findAll('div', class_='row', recursive=True)
        for rowElement in row:
            columns = rowElement.findAll('u')
            dataRow = [] 
            for columnElement in columns:
                dataRow.append(columnElement.string)
            # skip extraneous rows
            if dataRow[0][0:1] == '[':
                dataRows.append(dataRow)
    return dataRows

# MSP430 real FFT result has real part, imag part, real part, etc. order
def fftMagnitudes(samples):
    result = []
    i = 0
    limit = len(samples) - 1
    while i < limit:
        result.append(math.sqrt(samples[i]**2 + samples[i+1]**2))
        i = i + 2
    return result
