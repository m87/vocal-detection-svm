#!/usr/bin/env python
# encoding: utf-8

import wavio
import sys
from glob import glob



class Dataset(object):

    """Docstring for Data. """

    def __init__(self, directory):
        self.directory = directory

    def validationTracks(self):
        for filename in glob(self.directory+"/valid" + "/*.ogg"):
            yield filename

    def trainTracks(self):
        for filename in glob(self.directory+"/train" + "/*.ogg"):
            yield filename

    def testTracks(self):
        for filename in glob(self.directory+"/test" + "/*.ogg"):
            yield filename
    
    def adnotations(self):
        for filename in glob(self.directory+"/jamendo_lab" + "/*.lab"):
            yield filename





class VocalDetector(object):

    """Docstring for VocalDetector. """

    def __init__(self):
        """TODO: to be defined1. """
        pass


def main(path):
    ds = Dataset(path)
    for a in ds.adnotations():
        print(a)
    for a in ds.testTracks():
        print(a)
    for a in ds.trainTracks():
        print(a)
    for a in ds.validationTracks():
        print(a)







if __name__ == '__main__':
    main(sys.argv[1])
