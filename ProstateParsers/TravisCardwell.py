#!/usr/bin/env python

##############################################################################
# SimpleParser.py: a simple CoPATH-Parser parser
##############################################################################
#
# Author: Travis Cardwell <travis.cardwell@yuzutechnology.com>
#
##############################################################################

"""
This is a simple parser for the CoPATH-Parser project.  The existing parser
uses the pyparsing library, but such a library may not be easy to use by
someone without previous experience in parsing, especially with this input
data.  This example shows how to parse the data by hand, using only string
functions and regular expressions.

If this file is executable, it can be used as follows:

    $ ./SimpleParser.py tests/TestCases.txt out.csv

Otherwise, it can be executed as follows:

    $ python SimpleParser.py tests/TestCases.txt out.csv

The output differs from DesiredOutput.csv as follows:

* line 12: DesiredOutput.csv has a typo: '/' instead of ','
* line 16: DesiredOutput.csv Total != Primary + Secondary (error?)

This file is written to be compatible with Python 2.6.x, 2.7.x, and 3.x.
"""


import os
import re
import sys


__version__ = '0.0.1'


##############################################################################
# library

class CaseFileParser:

    def __init__(self, estream=None):
        """
        Initialize the parser

        :param file estream: stream to print errors to (default: None)
        """
        self.estream = estream
        # following regex validates the date format
        self.re_date = re.compile(r'^\d\d/\d\d/\d\d$')
        # following regex validates the case number format
        self.re_casenum = re.compile(r'^S\d\d-\d+$')
        # following regex validates the FMP format
        self.re_fmp = re.compile(r'^\d\d/\d\d\d-\d\d-\d\d\d\d$')
        # following regex extracts integers surrounding a + (ignoring spaces)
        self.re_gleason = re.compile(r'(\d+)\s*\+\s*(\d+)')

    def init_file(self, infile):
        """
        Initialize file references

        :param file infile: file to read case data from
        """
        self.infile = infile
        self.linenum = 0
        self.next_line()

    def next_line(self):
        """
        Proceed to the next line in the input file
        """
        try:
            self.line = next(self.infile)
            self.linenum += 1
        except StopIteration:
            self.line = None

    def next_case(self):
        """
        Skip to the beginning of the next case in the input file

        Lines starting a case begin with the date.  Other lines are indented
        or or blank.
        """
        self.next_line()
        while (self.line is not None and self.line[0] in ' \t\r\n'):
            self.next_line()

    def error(self, msg):
        """
        Display an error message, if enabled

        :param str msg: message to display
        """
        if self.estream is not None:
            self.estream.write("error: %s (line %d; skipping)%s" %
                               (msg, self.linenum, os.linesep))

    def parse_file(self, infile):
        """
        Parse a case file

        :param file infile: case file
        :returns: list of case rows
        :rtype: list of tuple of str
        """
        cases = []
        self.init_file(infile)
        while self.line is not None:
            # case should start with a date
            date, s, line = self.line.partition(' ')
            if not self.re_date.match(date):
                self.error("unable to read date")
                self.next_case()
                continue
            # after spaces, there should be a case number
            casenum, s, line = line.lstrip().partition(' ')
            if not self.re_casenum.match(casenum):
                self.error("unable to read case number")
                self.next_case()
                continue
            # after spaces, there should be a FMP
            fmp, s, line = line.lstrip().partition(' ')
            if not self.re_fmp.match(fmp):
                self.error("unable to read FMP")
                self.next_case()
                continue
            # initialize block count
            block = 0
            # special case: first line has tumor grades
            if self.line.find('GLEASON') > 0:
                mo = self.re_gleason.search(self.line)
                if mo is None:
                    self.error("unable to read tumor grades")
                else:
                    block += 1
                    grade1 = int(mo.group(1))
                    grade2 = int(mo.group(2))
                    gradeT = grade1 + grade2
                    cases.append((date, casenum, str(block), fmp,
                                  str(grade1), str(grade2), str(gradeT)))
            # proceed to second line of current case
            self.next_line()
            # process all lines for the current case
            while self.line is not None and self.line[0] in ' \t\r\n':
                # this line has tumor grades
                if self.line.find('GLEASON') > 0:
                    mo = self.re_gleason.search(self.line)
                    if mo is None:
                        self.error("unable to read tumor grades")
                    else:
                        block += 1
                        grade1 = int(mo.group(1))
                        grade2 = int(mo.group(2))
                        gradeT = grade1 + grade2
                        cases.append((date, casenum, str(block), fmp,
                                      str(grade1), str(grade2), str(gradeT)))
                self.next_line()
            # display an error if no tumor grades where found
            if block < 1:
                self.error("no tumor grades found in previous case")
        return cases


def write_csv(cases, outfile):
    """
    Write cases to CSV format

    :param tuple cases: case column strings
    :param file outfile: file to write to
    """
    outfile.write("#Columns:\n")
    outfile.write("#Date\n")
    outfile.write("#Case number\n")
    outfile.write("#Block (sequential, count 1, then only count if there " +
                  "is another gleason score in the same case)\n")
    outfile.write("#FMP (prefix+SSN)\n")
    outfile.write("#Primary tumor grade\n")
    outfile.write("#Secondary tumor grade\n")
    outfile.write("#Total (sum) tumor grade\n")
    outfile.write("\n")
    for case in cases:
        outfile.write(','.join(case) + '\n')


##############################################################################
# command line interface

def error_exit(msg):
    """
    Display a program error and exit

    :param str msg: message to display
    """
    sys.stderr.write("error: %s%s" % (msg, os.linesep))
    sys.exit(2)


def main(args=None):
    """
    CLI utility implementation

    :param list args: program arguments (default: sys.argv[1:])
    """
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] INFILE OUTFILE',
                          description='simple parser example',
                          version=('%prog ' + __version__))
    opts, args = parser.parse_args(args)
    if len(args) != 2:
        parser.error("not given two arguments")
    if not os.path.isfile(args[0]):
        error_exit("cannot find %s" % args[0])
    if not os.access(args[0], os.R_OK):
        error_exit("cannot read %s" % args[0])
    if os.path.isfile(args[1]):
        error_exit("%s already exists" % args[1])
    parent_dir = os.path.dirname(os.path.abspath(args[1]))
    if not os.access(parent_dir, os.W_OK):
        error_exit("cannot write to %s" % parent_dir)
    try:
        case_parser = CaseFileParser(sys.stderr)
        with open(args[0]) as infile:
            cases = case_parser.parse_file(infile)
        with open(args[1], 'w') as outfile:
            write_csv(cases, outfile)
    except IOError as e:
        error_exit("IO error: " + str(e))
    except OSError as e:
        error_exit("OS error: " + str(e))


if __name__ == '__main__':
    main()
