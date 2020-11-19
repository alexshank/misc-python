# needed libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from math import log10, inf
import helpers as h

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
h.printVal('NyQuist (Hz)', NyQuist)
h.printVal('Fs (Hz)', Fs)
h.printVal('Sampling period (sec)', samplingPeriod)
h.printVal('Samples (N)', N)
h.printVal('Total sample time (sec)', sampling_time)
h.printVal('Bin size (Hz)', binSize)
h.printVal('Worst Error (+-Hz)', worstError)
h.printVal('Rect -3dB Res (Hz)', human_resolution)
print()

# print bins that note frequencies should fall in 
criticalIndices = []
for note in notes:
    closestIndex = h.closestBin(note, binFreqs)
    criticalIndices.append(closestIndex)
    print('Closest bins to {}: '.format(note), end='')
    for i in range(-1, 2, 1):
        index = closestIndex + i
        print('[({}) {}]'.format(index, round(binFreqs[index], 1)), end='')
    print()
print()


# design least-squared error LP FIR filter [0 - 500 Hz]
taps = 31 
bands = [0, 500, 550, Fs / 2]
desired = [1, 1, 0, 0]
coeffs = signal.firls(taps, bands, desired, fs=Fs)
freq, response = signal.freqz(coeffs)
plt.figure(1)
plt.plot(freq*Fs/2/np.pi, 20*np.log10(abs(response) / max(abs(response))))
plt.title('FIR Filter Response (N={})'.format(taps))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude Response (dB)')

# print filter coefficients
print('FIR LP Filter Coefficients')
for coeff in coeffs:
    print(coeff)
print()

# create test samples and filter them
t = np.arange(0, sampling_time, samplingPeriod)
samples = h.createTones(t, [20, 500, 700])
filteredSamples = signal.lfilter(coeffs, 1, samples)

# plot filtering effects
[x_freq, y_freq] = h.getOneSidedFFT(samples, N, Fs)
[x_freq_filtered, y_freq_filtered] = h.getOneSidedFFT(filteredSamples, N, Fs)
fig, ax = plt.subplots(2)
ax[0].plot(x_freq, y_freq)
ax[1].plot(x_freq_filtered, y_freq_filtered)
fig.suptitle('Test Signal Filtering Effect')
for ax in ax.flat:
    ax.set(xlabel='Frequency (Hz)', ylabel='Magnitude Response (dB)')
    ax.label_outer()

# create test samples that are close together
t = np.arange(0, sampling_time, samplingPeriod)
samples = h.createTones(t, [80.5, 82.5])
[x_freq, y_freq] = h.getOneSidedFFT(samples, N, Fs)

# plot frequency resolution
plt.figure(3)
y_freq = y_freq[25:round(N/2) - 225]
x_freq = x_freq[25:round(N/2) - 225]
plt.plot(x_freq, y_freq, 'b-', label='FFT Result')
plt.plot([79, 86], [-3, -3], label='-3 dB Cutoff')
plt.title('Frequency Resolution of FFT (81.5 & 82.5 Hz Tones)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude Response (dB)')
plt.legend(loc='upper left')
plt.show()
