# needed libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from math import log10

### START UTIL FUNCTIONS ###
# util printing function
def printVal(text, val):
    print(text + ': {val}'.format(val=round(val, 2)))

# determine which bin frequency is closest to given note
def closestBin(note):
    lowestDiff = 10e4
    closestIndex = 0
    for i in range(0, len(binFreqs[0:int(N/2)])):
        if(abs(note - binFreqs[i]) < lowestDiff):
            lowestDiff = abs(note - binFreqs[i])
            closestIndex = i
    return closestIndex

# create cosines using time vector t and given frequencies
def createTones(t, frequencies):
    result = np.zeros(np.size(t))
    for frequency in frequencies:
        result = result + np.cos(frequency * 2 * np.pi * t)
    return result
    
# return N length one-sided FFT of passed in samples
def getOneSidedFFT(samples, N):
    y_freq = np.abs(np.fft.fft(samples, N))
    y_freq = y_freq[:round(N/2)] / N * 2
    x_freq = np.fft.fftfreq(N, d=1/Fs)[:round(N/2)]
    return [x_freq, y_freq]
### END UTIL FUNCTIONS ###

# controllable sampling parameters
human_resolution = 3.6                  # humans can notice 3.6 Hz differences
N = 512                                 # N = M (no zero padding for interpolation)
notes = [82, 110, 147, 196, 247, 330]   # standard tuning frequencies

# calculated FFT characteristics
Fs = human_resolution / 1.2 * N
NyQuist = max(notes) * 2
binFreqs = np.fft.fftfreq(N, d=1 / Fs)
samplingPeriod = 1 / Fs
sampling_time = samplingPeriod * N
binSize = Fs / N
worstError = binSize / 2

# display FFT chracteristics
printVal('NyQuist (Hz)', NyQuist)
printVal('Fs (Hz)', Fs)
printVal('Sampling period (sec)', samplingPeriod)
printVal('Samples (N)', N)
printVal('Total sample time (sec)', sampling_time)
printVal('Bin size (Hz)', binSize)
printVal('Worst Error (+-Hz)', worstError)
printVal('Rect -3dB Res (Hz)', human_resolution)
print()

# print bins that note frequencies should fall in 
criticalIndices = []
for note in notes:
    closestIndex = closestBin(note)
    criticalIndices.append(closestIndex)
    print('Closest bins to {} are [{}][{}][{}]'.format(
        note, round(binFreqs[closestIndex - 1], 1), round(binFreqs[closestIndex], 1), round(binFreqs[closestIndex + 1], 1)))
print()


# design least-squared error LP FIR filter [0 - 500 Hz]
taps = 31 
bands = [0, 500, 550, Fs / 2]
desired = [1, 1, 0, 0]
coeffs = signal.firls(taps, bands, desired, fs=Fs)
freq, response = signal.freqz(coeffs)
plt.figure(1)
plt.plot(freq*Fs/2/np.pi, abs(response))
plt.title('FIR Filter Response (N={})'.format(taps))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude Response')

# create test samples and filter them
t = np.arange(0, sampling_time, samplingPeriod)
samples = createTones(t, [30, 500, 600])
filteredSamples = signal.lfilter(coeffs, 1, samples)

# plot filtering effects
[x_freq, y_freq] = getOneSidedFFT(samples, N)
[x_freq_filtered, y_freq_filtered] = getOneSidedFFT(filteredSamples, N)
fig, ax = plt.subplots(2)
ax[0].plot(x_freq, y_freq)
ax[1].plot(x_freq_filtered, y_freq_filtered)
fig.suptitle('Test Signal Filtering Effect')
for ax in ax.flat:
    ax.set(xlabel='Frequency (Hz)', ylabel='Magnitude Response')
    ax.label_outer()

# create test samples that are close together
t = np.arange(0, sampling_time, samplingPeriod)
samples = createTones(t, [80, 85])
[x_freq, y_freq] = getOneSidedFFT(samples, N)

# plot frequency resolution
plt.figure(3)
y_freq = y_freq[25:round(N/2) - 225]
x_freq = x_freq[25:round(N/2) - 225]
plt.plot(x_freq, y_freq, 'bo')
plt.title('Frequency Resolution of FFT')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude Response')
plt.show()
