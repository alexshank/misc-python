import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack

# how many samples of a sample wave to plot
WAVE_LEN = 50

# plot fft of sampled signal
def fftPlot(axis, xf, yf, fs):
    axis.plot(xf, yf)
    axis.set_title('FFT (Fs = ' + str(fs) + ' Hz)')
    axis.set(xlabel='Frequency (Hz)', ylabel='Amplitude')

# plot original sin wave with samples shown
# TODO fix this plotting issue to show sampling effect
def samplePlot(axis, x, y, fs, f_sin):
    fs_ideal = 10000
    n = 3 * fs / f_sin
    n2 = fs_ideal / f_sin * 3
    x_ideal = np.linspace(0, n / fs_ideal, n - 1)
    y_ideal = np.sin(f_sin * 2 * np.pi * x_ideal)
    axis.plot(x_ideal, y_ideal)
    axis.plot(x[:n2], y[:n2], marker='o')
    axis.set_title('Original ' + str(f_sin) + ' Hz Sin Wave')
    axis.set(xlabel='Time (sec)', ylabel='Amplitude')

# sample a given sin wave and create its FFT
def getWaveAndFFT(N, fs, f_sin):
    # create wave from parameters
    x = np.linspace(0, N / fs, N - 1)
    y = np.sin(f_sin * 2 * np.pi * x)

    # fft of sampled sin wave
    xf = np.linspace(- fs / 2, fs / 2, N - 1, endpoint=False)
    yf = abs(scipy.fftpack.fft(y))
    yf = [w / fs for w in yf]   # account for sampling scaling
    yf = scipy.fftpack.fftshift(yf)
    return [x, y, xf, yf]

# sampling 500 hz sin wave at 4000 hz
N = 8000 
f_sin = 500
fs1 = 4000
[x, y, xf, yf] = getWaveAndFFT(N, fs1, f_sin)

# sampling 500 hz sin wave at 750 hz
fs2 = 800
[x1, y1, xf1, yf1] = getWaveAndFFT(N, fs2, f_sin)

# plot sampled sin wave and fft results
fig, axs = plt.subplots(2, 2)
fig.suptitle('FFT of 500 Hz Sin Wave')
samplePlot(axs[0, 0], x, y, fs1, f_sin)
fftPlot(axs[1, 0], xf, yf, fs1)
samplePlot(axs[0, 1], x1, y1, fs2, f_sin)
fftPlot(axs[1, 1], xf1, yf1, fs2)
plt.show()