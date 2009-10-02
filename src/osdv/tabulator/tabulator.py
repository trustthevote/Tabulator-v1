#!/usr/bin/env python
# Python 2.6.2
# Name: tabulator.py
# Author: Mike Anderson
# Created: Aug 5, 2009
# Purpose: To define a class that takes as input a merged BallotInfo 
#  file and generates a report

import yaml
import sys

import audit_header

class Tabulator(object):
    def __init__(self, input_file):
        # Load ballot records from yaml file
        try:
            stream = open(input_file + '.yaml', 'r')
        except:            
            print('Unable to open ' + input_file + '\n')
            exit(0)            
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            self.b = yaml.load_all(stream)

        # Add the vote counts of candidates with the same ID# using
        #  sumation(). Write the vote totals for each candidate to the
        #  report stream.
        s = self.sumation()
        print s

    # Sums up the separate vote counts in each record for each candidate
    #  and returns the cumulative result as a dictionary.
    def sumation(self):
        sum_dict = {}
        for rec in self.b:     
            for i in range(len(rec['contests'])):
                for j in range(len(rec['contests'][i]['candidates'])):
                    c_name = rec['contests'][i]['candidates'][j]['display_name']
                    if not sum_dict.has_key(c_name):
                        sum_dict[c_name] = 0                    
                    c_count = rec['contests'][i]['candidates'][j]['count']
                    sum_dict[c_name] += c_count
        return sum_dict

    # Serializes a dictionary into .csv format
    def serialize_csv(self):
        return
        
def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 2 ):
        print "Usage: [MERGED INPUT FILE]"
        exit()

    t = Tabulator(sys.argv[1])

    print 'SOVC report created in ' + sys.argv[1] + '_report.csv\n'

    return 0

if __name__ == '__main__': main()
