import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
plt.style.use('seaborn')


def getSamplesAndFFT(N, fs, f_sin):
    # create wave samples from parameters
    x = np.linspace(0, N / fs, N - 1)
    y = np.sin(f_sin * 2 * np.pi * x)

    # fft of sampled sin wave
    xf = np.linspace(- fs / 2, fs / 2, N - 1)
    yf = scipy.fftpack.fft(y)
    yf = [w / fs for w in yf]   # account for sampling scaling
    yf = scipy.fftpack.fftshift(yf)
    return [x, y, xf, yf]


def samplePlot(axis, x, y, fs, f_sin):
    # display first three periods of original signal
    fs_ideal = 10000
    n_display = int(fs_ideal / f_sin * 3)
    x_ideal = np.linspace(0, n_display / fs_ideal, n_display)
    y_ideal = np.sin(f_sin * 2 * np.pi * x_ideal)
    axis.plot(x_ideal, y_ideal)

    # display samples taken from three periods of signal
    n_display = int(3 * fs / f_sin)
    axis.plot(x[:n_display + 1], y[:n_display + 1], 'ro')
    axis.set(xlabel='Time (sec)', ylabel='Amplitude')


def fftPlot(real_axis, angle_axis, xf, yf, fs):
    real_axis.plot(xf, np.absolute(yf))
    real_axis.set(xlabel='Frequency (Hz)', ylabel='Magnitude')
    angle_axis.plot(xf, np.angle(yf))
    angle_axis.set(xlabel='Frequency (Hz)', ylabel='Angle')


# number of samples and analog wave frequency
f_sin = 500
N = 10000
fs = 4000
[x, y, xf, yf] = getSamplesAndFFT(N, fs, f_sin)

# plot oversampled sin wave and fft results
fig, axs = plt.subplots(3, 1)
fig.suptitle('FFT of ' + str(f_sin) + ' Hz Sin Wave (Fs=' + str(fs) + ')')
samplePlot(axs[0], x, y, fs, f_sin)
fftPlot(axs[1], axs[2], xf, yf, fs)

# undersampling 500 hz sin wave at 800 hz
fs2 = 800
[x1, y1, xf1, yf1] = getSamplesAndFFT(N, fs2, f_sin)

# plot undersampled sin wave and fft results
fig2, axs2 = plt.subplots(3, 1)
fig2.suptitle('FFT of ' + str(f_sin) + ' Hz Sin Wave (Fs=' + str(fs2) + ')')
samplePlot(axs2[0], x1, y1, fs2, f_sin)
fftPlot(axs2[1], axs2[2], xf1, yf1, fs2)

# plot the 500 hz signal sampled at 800 hz (same as earlier)
figure, axis = plt.subplots()
samplePlot(axis, x1, y1, fs2, f_sin)

# superimpose the 300 hz wave
f_sin_300 = 300
fs_ideal = 10000
x = np.linspace(0, N / fs_ideal, N - 1)
y = np.sin(f_sin_300 * 2 * np.pi * x - np.pi)
y = [w * 1 for w in y]
t = int(2 * fs_ideal / f_sin_300)
axis.plot(x[:t], y[:t])
plt.show()
