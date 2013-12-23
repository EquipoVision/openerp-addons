import unittest
import subprocess
import os
import select
import time
import json
from openerp import tools

ROOT = os.path.join(os.path.dirname(__file__), 'ui_suite')

__all__ = ['load_tests', 'WebsiteUiSuite']

def _exc_info_to_string(err, test):
    return err

class LineReader:
    def __init__(self, fd):
        self._fd = fd
        self._buf = ''

    def fileno(self):
        return self._fd

    def readlines(self):
        data = os.read(self._fd, 4096)
        if not data:
            # EOF
            return None
        self._buf += data
        if '\n' not in data:
            return []
        tmp = self._buf.split('\n')
        lines, self._buf = tmp[:-1], tmp[-1]
        return lines

class WebsiteUiTest(unittest.TestCase):
    def __init__(self, name):
        self.name = name
    def shortDescription(self):
        return None
    def __str__(self):
        return self.name

class WebsiteUiSuite(unittest.TestSuite):
    # timeout is in seconds
    def __init__(self, testfile, timeout=5):
        self.testfile = testfile
        self.timeout = timeout
        self._test = None

    def __iter__(self):
        return iter([self])

    def run(self, result):
        # Test if phantom is correctly installed
        try:
            subprocess.call([
                'phantomjs',
                '-v'
            ],
            stdout=open(os.devnull, 'w'),
            stderr=subprocess.STDOUT)
        except OSError:
            test = WebsiteUiTest('UI Tests')
            result.startTest(test)
            result.addSkip(test, "phantomjs command not found")
            result.stopTest(test)
            return

        result._exc_info_to_string = _exc_info_to_string
        try:
            self._run(result)
        finally:
            del result._exc_info_to_string

    def _run(self, result):
        self._test = WebsiteUiTest(self.testfile)
        self.start_time = time.time()
        last_check_time = time.time()

        phantomOptions = json.dumps({
            'timeout': self.timeout,
            'port': tools.config['xmlrpc_port']
        })

        phantom = subprocess.Popen([
            'phantomjs',
            os.path.join(ROOT, self.testfile),
            phantomOptions
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
        proc_stdout = LineReader(phantom.stdout.fileno())
        readable = [proc_stdout]
        try:
            while readable and last_check_time < self.start_time + self.timeout:
                ready, _, _ = select.select(readable, [], [], 0.1)
                if not ready:
                    last_check_time = time.time()
                    continue
                for stream in ready:
                    lines = stream.readlines()
                    if lines is None:
                        # got EOF on this stream
                        readable.remove(stream)
                        break;
                    for line in lines:
                        self.process(line, result)
                        # the runner expects only one output line
                        # any subsequent line is ignored
                        break
            if last_check_time >= (self.start_time + self.timeout):
                result.addError(self._test, "Timeout after %s s" % (last_check_time - self.start_time ))
            result.stopTest(self._test)
        finally:
            # kill phantomjs if phantom.exit() wasn't called in the test
            if phantom.poll() is None:
                phantom.terminate()

    def process(self, line, result):
        # Test protocol
        # -------------
        # use console.log in phantomjs to output test results using the following format:
        # - for a success: { "event": "success" }
        # - for a failure: { "event": "failure", "message": "Failure description" }
        # any other message is treated as an error
        result.startTest(self._test)
        try:
            args = json.loads(line)
            event = args.get('event', None)
            if event == 'success':
                result.addSuccess(self._test)
            elif event == 'failure':
                message = args.get('message', "")
                result.addFailure(self._test, message)
            else:
                result.addError(self._test, "Unexpected message: %s" % line)
        except ValueError:
             result.addError(self._test, "Unexpected message: %s" % line)

def load_tests(loader, base, _):
    base.addTest(WebsiteUiSuite('sample_test.js'))
    base.addTest(WebsiteUiSuite('banner_tour.js'))
    return base