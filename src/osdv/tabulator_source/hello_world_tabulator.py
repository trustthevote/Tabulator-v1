#!/usr/bin/env python

"""
Developed with Python 2.6.2
Name: hello_world_tabulator.py
Author: Mike Anderson
Created: Aug 14, 2009
Purpose: A precursor to a fully functional tabulator, this starter
 simply takes four parameters, the last of which will be the filename of
 a file containing "Hello Tabulator" in it.
"""

from __future__ import with_statement
import sys

class HWTabulator(object):
    def __init__(self, arg1, arg2, arg3, dest_file):
        with open(dest_file, 'w') as stream:
            stream.write('Hello World!\n')

def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 5 ):
        print "Usage: [FILE1] [FILE2] [FILE3] [DESTINATION FILE]"       
        exit()
    
    t = HWTabulator(*sys.argv[1:])
    print "Created file " + sys.argv[4]
    
    return 0

if __name__ == '__main__': main()
