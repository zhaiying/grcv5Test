
from unittest.main import TestProgram


class SmartTestProgram(TestProgram):

    def parseArgs(self, argv):
        if len(argv) > 1 and argv[1].lower() == 'discover':
            self._do_discovery(argv[2:])
            return
        
		
        import getopt
        long_opts = ['help', 'verbose', 'quiet', 'failfast', 'catch', 'buffer']
        try:
            options, args = getopt.getopt(argv[1:], 'hHvqfcb', long_opts)
            for opt, value in options:
                if opt in ('-h','-H','--help'):
                    self.usageExit()
                if opt in ('-q','--quiet'):
                    self.verbosity = 0
                if opt in ('-v','--verbose'):
                    self.verbosity = 2
                if opt in ('-f','--failfast'):
                    if self.failfast is None:
                        self.failfast = True
                    # Should this raise an exception if -f is not valid?
                if opt in ('-c','--catch'):
                    if self.catchbreak is None:
                        self.catchbreak = True
                    # Should this raise an exception if -c is not valid?
                if opt in ('-b','--buffer'):
                    if self.buffer is None:
                        self.buffer = True
                    # Should this raise an exception if -b is not valid?
            if len(args) == 0 and self.defaultTest is None:
                # createTests will load tests from self.module
                self.testNames = None
            elif len(args) > 0:
                self.testNames = args
                if __name__ == '__main__':
                    # to support python -m unittest ...
                    self.module = None
            else:
                self.testNames = (self.defaultTest,)
            self.createTests()
        except Exception as msg:
            self.usageExit(msg)
main=SmartTestProgram