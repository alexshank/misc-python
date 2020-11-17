'''
Alex Shank - 11/11/20
Takes the HTML of the Code Composer Studio Cloud website and
parses debugging values generated by the ADC. Then generates a
CSV output with various conversion for analysis. Also plots
the values so that sampled signal can be verified.
'''

# beautiful soup parses HTML data for you
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# open the input file (that is manually copied from CCS Online)
with open('./Capstone/FDR_Report_Save_2/input.html', 'r') as f:
    data = f.read()
soup = BeautifulSoup(data, 'html.parser')

# get div containing debugging values
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

# compute signed int from given hex value
# (deprecated: unsigned ints now being used)
def twos_complement(hexstr,bits=16):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

# convert the ADC hex value into corresponding voltage
# formula found on page 871 of
# MSP430FR58xx, MSP430FR59xx, and MSP430FR6xx Family User's Guide (Rev. P)
def voltageRead(dec):
    VR_Pos = 3.3
    VR_Neg = 0
    V_In = dec / 4096 * (VR_Pos - VR_Neg)
    V_In = V_In + VR_Neg - (VR_Pos - VR_Neg) / 8192
    return V_In

# write CSV data to output file
f = open("./Capstone/output.csv", "w")
f.write('index, memory location, data type, hex value, dec, voltage\n')
experimental = []   # holds samples converted to voltages
for row in dataRows:
    f.write(row[0] + ', ')      # sample index
    f.write(row[3] + ', ')      # memory location of sample
    f.write(row[2] + ', ')      # data type of sample
    f.write(row[1] + ', ')      # hex value of sample

    # some values are already displayed in dec, some need converted from hex
    if('x' in row[1]):
        dec = int(row[1][2:], 16)   # dec value of sample
    else:
        dec = int(row[1])

    f.write(str(dec) + ', '),
    voltage = voltageRead(dec)  # voltage based off sample dec value
    f.write(str(voltage))
    experimental.append(voltage)
    f.write('\n')
f.close()

# plot results
Fs = 32768 / 4      # ADC is configured to this sample rate
t = np.linspace(0, 512 * 1 / Fs, 512, endpoint=False)
signal = 0.12 * np.cos(2 * np.pi * 500 * t) + 1.650
fig, ax = plt.subplots(2)
ax[0].plot(t, experimental, label='Sampled Signal')
ax[1].plot(t[300:350], signal[300:350], label='Generated Signal Zoomed')
ax[1].plot(t[300:350], experimental[300:350], label='Sampled Signal Zoomed')
ax[1].legend(loc='upper right')
ax[0].title.set_text('Microphone Verification (500 Hz Sin Wave)')
for ax in ax.flat:
    ax.set(xlabel='Time (Seconds)', ylabel='Voltage (V)')
    ax.label_outer()

# get one sided FFT of passed in signal
def getOneSidedFFT(samples, N, Fs):
    x_fft = np.fft.fftfreq(N, d=1/Fs)           # bin frequencies
    y_fft = np.abs(np.fft.fft(samples, N))      # ignore phase
    y_fft = y_fft / N * 2                       # double energy because left side eliminated
    y_fft = 20*np.log10(y_fft / max(y_fft))     # normalized dB magnitude
    return [x_fft[:round(N/2)], y_fft[:round(N/2)]]     # return only the right side

# plot FFTs to verify samples
plt.figure(2)
[x, y] = getOneSidedFFT(signal, len(signal), Fs)
[x1, y1] = getOneSidedFFT(experimental, len(experimental), Fs)
plt.plot(x, y, label='Generated Signal')
plt.plot(x1, y1, label='Sampled Signal')
plt.legend(loc='upper right')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Normalized Magnitude (dB)')
plt.title('Microphone Verification (500 Hz Sin Wave FFT)')
plt.show()
