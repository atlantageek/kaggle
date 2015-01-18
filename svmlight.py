import string
import numpy
import math
import subprocess

from driver import Driver

class SVMLight(object):
    def __init__(self, path_and_prefix, opts = {}):
        self.path_and_prefix = path_and_prefix
        self.memory = opts['memory'] if opts.has_key('memory') else 500
        self.model_type = opts['model_type'] if opts.has_key('model_type') else 2
        self.gamma = opts['gamma'] if opts.has_key('gamma') else 0.25

        self.path_to_learner = 'svm_learn'
        self.path_to_classifier = 'svm_classify'

        self.train_filename  = "%s-train.dat"  % (self.path_and_prefix)
        self.model_filename  = "%s-model.dat"  % (self.path_and_prefix)
        self.test_filename   = "%s-test.dat"   % (self.path_and_prefix)
        self.output_filename = "%s-output.dat" % (self.path_and_prefix)

    def training_params(self):
        return [
            self.path_to_learner,
            '-m', str(self.memory),
            '-t', str(self.model_type),
            '-g', str(self.gamma),
            self.train_filename,
            self.model_filename
        ]

    def testing_params(self):
        return [
            self.path_to_classifier,
            self.test_filename,
            self.model_filename,
            self.output_filename
        ]

    def load_output(self):
        with open(self.output_filename, 'rb') as f:
            output = numpy.array(map(float, map(string.strip, f.readlines())))

        return output


    def run(self, show_log = False):
        training_log = subprocess.check_output(self.training_params())
        testing_log  = subprocess.check_output(self.testing_params())

        if show_log is True:
            print training_log
            print testing_log

        return self.load_output()
