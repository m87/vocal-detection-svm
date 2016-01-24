#!/usr/bin/env python
# encoding: utf-8

import wavio
import sys
from glob import glob
from scipy.signal import decimate
from features import mfcc
import bisect
import random
import numpy as np
from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import audioFeatureExtraction

from sklearn import svm

class LabelTeller():

    """docstring for LabelTeller"""

    def __init__(self, firstLabel, blockLimits):
        self._firstLabel = firstLabel
        self._blockLimits = blockLimits
        self._secondLabel = 'sing' if 'nosing' == self._firstLabel else 'nosing'

    def tell(self, noOfBlock):
        index = bisect.bisect_left(self._blockLimits, noOfBlock)
        return self._firstLabel if 0 == (index % 2) else self._secondLabel

    def tellNoOfAllBlocks(self):
        return self._blockLimits[-1] + 1


class Loader():

    """docstring for Loader"""

    def __init__(self, labelDir, blockLength, overlap):
        # labelDir should end with /
        # blockLength is in ms
        self._labelDir = labelDir
        self._blockLength = blockLength / 1000.0
        self._overlap = overlap / 1000.0
        self._firstLabel = ''
        self._blockLimits = []

    def loadLabelsForSoundfile(self, soundFilename):
        self._blockLimits = []
        labelFilePath = self._labelDir+ "../jamendo_lab/"+ soundFilename.replace('.wav', '.lab')
        with open(labelFilePath, 'r') as f:
            intervalLimits = self.parse(f)
            self.transformTimeIntervalsToBlocks(intervalLimits)
        return LabelTeller(self._firstLabel, self._blockLimits)

    def parse(self, labelFile):
        intervalLimits = []
        line = labelFile.readline().split(' ')
        self._firstLabel = line[2].rstrip()
        intervalLimits.append(float(line[1]))
        for line in labelFile:
            intervalEnd = line.split(' ')[1]
            intervalLimits.append(float(intervalEnd))
        return intervalLimits

    def transformTimeIntervalsToBlocks(self, intervalLimits):
        for limit in intervalLimits:
            blockLimit = int(limit / (self._blockLength - self._overlap)) - 1
            # int not round because decimal is related to half of block
            self._blockLimits.append(blockLimit)



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

    #def windows(self,track, rate, width, overlap):
    #    wav = wavio.read(track)
    #    signal = decimate(wav.data[:, 0], wav.rate / rate)
    #    print wav.rate

        #for start in xrange(0, signal.shape[0] - width + overlap, overlap):
            #if start > overlap:
            #    start -= overlap

         #   yield signal[start:(start+width)]







class VocalDetector(object):

    """Docstring for VocalDetector. """

    def __init__(self):
        self.classifier = svm.SVC(cache_size=2000)



def main(path):
    ds = Dataset(path)
    loader = Loader(path+"/train/", 32,16)
    X = []
    y=[]
    Z= []
    ii = 0
    for p in ds.trainTracks():
        f=p.split("/")
        name = f[len(f)-1]
        labelTeller = loader.loadLabelsForSoundfile(name)
        [Fs, x] = audioBasicIO.readAudioFile(p)
        F = audioFeatureExtraction.stFeatureExtraction(x, Fs, 0.032*Fs, 0.016*Fs);
        G = zip(*F)
        N = 0
        if(len(G)>labelTeller.tellNoOfAllBlocks()):
            N = labelTeller.tellNoOfAllBlocks()
        else:
            N = len(G)

        for i in range(N):
            Z.append([G[i],labelTeller.tell(i)])
            

        #i = 0
        #for w in ds.windows(x,44100, 1410, 705):   
        #    mf = mfcc(w)
            #row = [i]
        #    Z.append([mf[0],labelTeller.tell(i)])
        #    i = i+1
            
        print p +" "+ str(ii)+"/61"
        ii = ii +1
    
    print "shuffle"
    random.shuffle(Z)
    Z = zip(*Z)    

    NN = 20000
    L = NN
    R = NN
    FINAL =[[],[]]
    for i in range(len(Z[0])):
        if(Z[1][i] == 'sing' and L>0 ):
            L = L - 1
            FINAL[0].append(Z[0][i])
            FINAL[1].append(Z[1][i])

        if(Z[1][i] == 'nosing' and R>0 ):
            R = R - 1
            FINAL[0].append(Z[0][i])
            FINAL[1].append(Z[1][i])



        

    clf = svm.SVC(cache_size=2000)
    print "######### " + str(len(Z[0]))
    clf.fit(FINAL[0], FINAL[1])
    loader = Loader(path+"/test/", 32,16)
    

    print "Loading test"
    for p in ds.validationTracks():
        X = []
        y=[]
        f=p.split("/")
        name = f[len(f)-1]
        labelTeller = loader.loadLabelsForSoundfile(name)
        i = 0
        
        [Fs, x] = audioBasicIO.readAudioFile(p)
        F = audioFeatureExtraction.stFeatureExtraction(x, Fs, 0.032*Fs, 0.016*Fs);
        G = zip(*F)
        N = 0
        if(len(G)>labelTeller.tellNoOfAllBlocks()):
            N = labelTeller.tellNoOfAllBlocks()
        else:
            N = len(G)

        for i in range(N):
            X.append(G[i])
            y.append(labelTeller.tell(i))
        
        print "Starting prediction "+p 
            
        Y= clf.predict(X)
        ok = 0
        al = 0
        for i in range(len(y)):
            if(y[i]==Y[i]):
                ok = ok +1
            al = al +1

        print ok/float(al)



         


        #for w in ds.windows(x,44100, 1410, 705):   
        #    mf = mfcc(w)
        #    #row = [i]
        #    X.append(mf[0])
        #    y.append(labelTeller.tell(i))
        #    i = i+1
            
    


if __name__ == '__main__':
    main(sys.argv[1])
