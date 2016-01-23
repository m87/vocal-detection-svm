#!/usr/bin/env python
# encoding: utf-8

import wavio
import sys
from glob import glob
from scipy.signal import decimate
from features import mfcc



class Dataset(object):

    """Docstring for Data. """

    def __init__(self, directory):
        self.directory = directory

    def validationTracks(self):
        for filename in glob(self.directory+"/valid" + "/*.wav"):
            yield filename

    def trainTracks(self):
        for filename in glob(self.directory+"/train" + "/*.wav"):
            yield filename

    def testTracks(self):
        for filename in glob(self.directory+"/test" + "/*.wav"):
            yield filename
    
    def adnotations(self):
        for filename in glob(self.directory+"/jamendo_lab" + "/*.lab"):
            yield filename

    def windows(self,track, rate, width, overlap):
        wav = wavio.read(track)
        signal = decimate(wav.data[:, 0], wav.rate / rate)


        for start in xrange(0, signal.shape[0] - width + overlap, width):
            if start > overlap:
                start -= overlap

            yield signal[start:(start+width)]







class VocalDetector(object):

    """Docstring for VocalDetector. """

    def __init__(self):
        self.classifier = svm.SVC(cache_size=2000)



def main(path):
    ds = Dataset(path)
    for a in ds.adnotations():
        print(a)
    for a in ds.testTracks():
        print(a)
    for a in ds.trainTracks():
        print(a)
    for a in ds.validationTracks():
        for w in ds.windows(a, 16000,512,256):
            print mfcc(w,16000, winlen=0.032)







if __name__ == '__main__':
    main(sys.argv[1])
