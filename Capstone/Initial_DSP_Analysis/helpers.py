import numpy as np

# printing function
def printVal(text, val):
    print(text + ': {val}'.format(val=round(val, 2)))

# determine which bin frequency is closest to given note
def closestBin(note, binFreqs):
    N = np.size(binFreqs)
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
def getOneSidedFFT(samples, N, Fs):
    y_freq = np.abs(np.fft.fft(samples, N))
    y_freq = y_freq[:round(N/2)] / N * 2
    y_freq_db = 20*np.log10(y_freq / max(y_freq))
    x_freq = np.fft.fftfreq(N, d=1/Fs)[:round(N/2)]
    return [x_freq, y_freq_db]