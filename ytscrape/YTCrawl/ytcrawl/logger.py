"""The logger class supporting the crawler."""

# pylama:ignore=D212,D213,E501

# Author: Honglin Yu <yuhonglin1986@gmail.com>
# License: BSD 3 clause


import time
import os
from os.path import join


class Logger(object):
    """record the crawling status, error and warnings."""

    def __init__(self, outputDir=""):
        """init."""
        self._output_dir = outputDir
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        self._log_file_dict = {'log': open(join(self._output_dir, 'log'), 'a+')}
        self._done_file = open(join(self._output_dir, 'key.done'), 'a+')

    def add_log(self, d):
        """Add a log file."""
        for i, j in d.items():
            self._log_file_dict[i] = open(join(self._output_dir, j), 'a+')

    def get_key_done(self, lfkl):
        """Get the keys that have been crawled."""
        r = []

        for i in lfkl:
            tmp = self._log_file_dict[i]
            for l in tmp:
                r.append(eval(l)[1])

        return r + [x.rstrip('\n') for x in self._done_file]

    def log_done(self, k):
        """Thread safe finalizer for logs."""
        # self._mutex_done.acquire()
        self._done_file.write('%s\n' % k)
        self._done_file.flush()
        # self._mutex_done.release()

    def log_warn(self, k, m, lfk='log'):
        """Log message as warning.

        Arguments:
        - `k` : the key
        - `m`: the message
        - `lfk`: log_file_key
        """
        # self._mutex_log.acquire()
        self._log_file_dict[lfk].write(str([time.strftime('%Y_%m_%d_%m_%H_%M'), k, m]) + '\n')
        self._log_file_dict[lfk].flush()
        # self._mutex_log.release()
