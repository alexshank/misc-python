# needed libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import signal

# TODO could make this a brute force least squared error problem (even using window functions)
# controllable parameters
Fs = 1200
M = 250 
N = 512
notes = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]
#notes = [82, 110, 146, 196, 246, 330]


# different frequency resolutions and total sampling time
bestRes = Fs / M
print('\nTheoretical resolution = {res} Hz'.format(res=round(bestRes, 2)))
rectRes = 1.2*Fs/M
print('Rectangular resolution = {res} Hz'.format(res=round(rectRes, 2)))
freqs = np.fft.fftfreq(N, d=1 / Fs)
print('Padded resolution = {res} Hz'.format(res=round(freqs[1], 2)))
print('Sampling time = {res} sec'.format(res=round(1 / Fs * M, 2)))
print()

# determine which bin frequency is closest to given note
def closestBin(note):
    lowestDiff = 10e4
    closestIndex = 0
    for i in range(0, len(freqs[0:int(N/2)])):
        if(abs(note - freqs[i]) < lowestDiff):
            lowestDiff = abs(note - freqs[i])
            closestIndex = i
    return closestIndex

# print bins that note frequencies should fall between
criticalIndices = []
for note in notes:
    closestIndex = closestBin(note)
    criticalIndices.append(closestIndex)
    print('Closest bin to {} is ({}) {} Hz'.format(note, closestIndex, freqs[closestIndex]))
print()

# run through all valid frequencies and test algorithm
largestErrors = [0, 0, 0, 0, 0, 0]
testFreqs = np.arange(0, 513, 0.1)
for testFreq in testFreqs:
    t = np.arange(0+0.3, M / Fs + 0.3, 1 / Fs)
    tone = lambda t: np.cos(testFreq * 2 * np.pi * t)
    y_freq = abs(np.fft.fft(tone(t), N)) 
    y_freq = y_freq[:round(N/2)] / N * 2 # normalize one sided fft amplitude
    x_freq = np.fft.fftfreq(N, d=1/Fs)[:round(N/2)]
    
    # track the largest possible error tuning could end at
    index = np.argmax(y_freq)
    for i in range(0, len(criticalIndices)):
        if index == criticalIndices[i]:
            diff = abs(x_freq[index] - testFreq)
            if(diff > largestErrors[i]):
                largestErrors[i] = diff

def numFormat(num):
    return str(round(num, 2)).zfill(6)

# print largest possible errors
for i in range(0, len(largestErrors)):
    print('{} - {}'.format(numFormat(notes[i]), numFormat(largestErrors[i])))
print('Worst total error: {} Hz\n'.format(numFormat(sum(largestErrors))))

# create a test signal with two close frequencies and high freq noise
t = np.arange(0, M / Fs, 1 / Fs)
testDiff = 4.5 
toneTest = lambda t: np.cos(80 * 2 * np.pi * t) + np.cos((80 + testDiff) * 2 * np.pi * t) + np.cos(1600 * 2 * np.pi * t)

# design least-squared error FIR filter
taps = 31
bands = [0, 500, 550, 600]
desired = [1, 1, 0, 0]
coeffs = signal.firls(taps, bands, desired, fs=Fs)
freq, response = signal.freqz(coeffs)
plt.subplot(131)
plt.plot(freq*Fs/2/np.pi, abs(response))

# take samples and filter them (filter is useless...)
samples = toneTest(t)
samples = signal.lfilter(coeffs, 1, samples)

# show theoretical resolution and filtering effects
plt.subplot(132)
y_freq = abs(np.fft.fft(samples, N)) 
y_freq = y_freq[:round(N/2)] / N * 2 # normalize one sided fft amplitude
x_freq = np.fft.fftfreq(N, d=1/Fs)[:round(N/2)]
plt.plot(x_freq, y_freq)#, 'bo')
plt.subplot(133)
y_freq = y_freq[25:round(N/2) - 200]
x_freq = x_freq[25:round(N/2) - 200]
plt.plot(x_freq, y_freq)#, 'bo')
plt.show()
