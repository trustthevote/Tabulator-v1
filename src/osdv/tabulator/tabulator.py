#!/usr/bin/env python
# Python 2.6.2
# Name: tabulator.py
# Author: Mike Anderson
# Created: Aug 5, 2009
# Purpose: To define a class that takes

import yaml
import sys

# Checks validity of two ballot record files against some election
#  specs, merges them together, and generates a report.
class Tabulator(object):
    def __init__(self, election_file, record_file1, record_file2,
                 merge_output_file, report_output_file):
        # Open a stream to a report file that will be written to during
        #  the course of tabulation.
        self.rstream = open(report_output_file, 'w')
        
        # Load ballot records from yaml file
        try:
            stream = open(record_file1 + '.yaml', 'r')
        except:
            self.rstream.write('Unable to open ' + record_file1 + '\n')
            print('Unable to open ' + record_file1 + '\n')
            exit()
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid1 = a.file_id
            prov1 = a.provenance
            self.b1 = list(yaml.load_all(stream))

        # Add the vote counts of candidates with the same ID# using
        #  sumation(). Write the vote totals for each candidate to the
        #  report stream.
        s = self.sumation()
        self.rstream.write('\n')
        for key in s.keys():
            self.rstream.write(str(s[key]) + ' votes found for ' + key + '\n')

        stream.close()
        self.rstream.close()

    # Sums up the separate vote counts in each record for each candidate
    #  and returns the cumulative result as a dictionary.
    def sumation(self):
        sum_dict = {}
        for file in (self.b1, self.b2):
            for rec in file:     
                for i in range(len(rec['contests'])):
                    for j in range(len(rec['contests'][i]['candidates'])):
                        c_name = rec['contests'][i]['candidates'][j]['display_name']
                        if not sum_dict.has_key(c_name):
                            sum_dict[c_name] = 0                    
                        c_count = rec['contests'][i]['candidates'][j]['count']
                        sum_dict[c_name] += c_count
        return sum_dict

def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 6 ):
        print "Usage: [ELECTION SPECS FILE] [BALLOT RECORD FILE 1]",
        print "[BALLOT RECORD FILE 2] [MERGED OUTPUT FILE]", 
        print "[REPORT OUTPUT FILE]"
        exit()

    t = Tabulator(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                  sys.argv[5])

    print "Successfully merged " + sys.argv[2] + " and " + sys.argv[3],
    print "together\n The result is stored in " + sys.argv[4] + ".yaml",
    print "and " + sys.argv[4] + ".xml"
    print "A report describing attributes of the merge was created",
    print "in " + sys.argv[5]

    return 0

if __name__ == '__main__': main()
