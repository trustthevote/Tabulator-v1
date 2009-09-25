#!/usr/bin/env python
# Python 2.6.2
# Name: tabulator.py
# Author: Mike Anderson
# Created: Aug 5, 2009
# Purpose: To define a class that merges two ballot record files
#  together into one file.

import yaml
import sys
import uuid
from plistlib import writePlistToString as xmlSerialize

import audit_header

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
        try:
            stream = open(record_file2 + '.yaml', 'r')
        except:
            self.rstream.write('Unable to open ' + record_file2 + '\n')
            print('Unable to open ' + record_file2 + '\n')
            exit()
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid2 = a.file_id
            prov2 = a.provenance
            
            self.b2 = list(yaml.load_all(stream))

        # Get the election specs from file
        stream = open(election_file + '.yaml', 'r')
        for i in range(0,8):  # Ignore the audit header
            stream.readline()
        self.e = yaml.load(stream)
        
        print self.e.keys()
        print self.e['contests'][0].keys()
        print self.e['contests'][0]['candidates'][0].keys()
        exit()

        # Perform some error checks on the input data for robustness
        self.validate()

        # Combine provenances and guids from input files
        new_prov = []
        new_prov.extend(prov1)
        new_prov.extend(prov2)
        new_prov.append(guid1)
        new_prov.append(guid2)        

        # If the same GUID appears twice, then abort the merge
        for guid in new_prov:
            if new_prov.count(guid) > 1:
                print "Input files contain the same ballot record,",
                "merge aborted\n"
                self.rstream.write(
                    "Input files contain the same ballot record,",
                    "merge aborted\n")
                exit()

        # Add the vote counts of candidates with the same ID# using
        #  merge(). Write the vote totals for each candidate to the
        #  report stream.
        s = self.sumation()
        self.rstream.write('\n')
        for key in s.keys():
            self.rstream.write(str(s[key]) + ' votes found for ' + key + '\n')

        # Create an audit header for merge file
        a = audit_header.AuditHeader()
        a.set_fields('tabulator_aggregation',
                     'Pito Salas', 'TTV Tabulator TAB02', 
                     'TTV Tabulator 1.2 JUL-1-2008', new_prov)

        # Dump merge into a file in yaml format
        stream = open(merge_output_file + '.yaml', 'w')
        stream.write(a.serialize_yaml())
        yaml.dump_all(self.b1, stream)
        stream.write('---\n')
        yaml.dump_all(self.b2, stream)

        # Dump merge into a file in xml format        
        stream = open(merge_output_file + '.xml', 'w')
        stream.write(a.serialize_xml())
        for record in self.b1:
            stream.writelines(xmlSerialize(record)[173:]. \
                replace('\t', '    ').replace('\n</plist>', ''))
        for record in self.b2:
            stream.writelines(xmlSerialize(record)[173:]. \
                replace('\t', '    ').replace('\n</plist>', ''))

        stream.close()
        self.rstream.close()


    # Check to see that all input data is valid
    def validate():
        self.verify_match_record(self)
        self.verify_data_structures(self)
        #self.verify_fields(self)

    # Verify that the two ballot record files are consistent with the
    #  given election
    def validate_match_election(self):
        # Match the values in each record from both record files to the
        #  election specs. If any pair of values do not match, return
        #  the number (1 or 2) of the offending record file. Otherwise
        #  return 0
        for b in self.b1:
            if ((b['election_name'] != self.e['election_name']) or
            (len(b['contests']) != len(self.e['contests']))):             
                print "First record file did not match election",
                "template, merge aborted\n"
                self.rstream.write("First record file did not match election template, merge aborted\n")
                exit()
            for i in range(len(self.e['contests'])):
                if not self.match_contest(self.e['contests'][i],
                                          b['contests'][i]):
                    print "First record file did not match election",
                    "template, merge aborted\n"
                    self.rstream.write("First record file did not match election template, merge aborted\n")
                    exit()
        for b in self.b2:
            if (b['election_name'] != self.e['election_name']) or \
            (len(b['contests']) != len(self.e['contests'])):
                print "Second record file did not match election",
                "template, merge aborted\n"
                self.rstream.write("Second record file did not match election template, merge aborted\n")
                exit()
            for i in range(len(self.e['contests'])):
                if not self.match_contest(self.e['contests'][i], 
                                          b['contests'][i]):
                    print "Second record file did not match election",
                    "template, merge aborted\n"
                    self.rstream.write("Second record file did not match election template, merge aborted\n")
                    exit()
        self.rstream.write("Both record files matched election template.\n")

    # Verify that the three input files all contain data structures that
    #  are consistent with the BallotInfo specs, a data structure should
    #  not contain more fields than the specs, nor should it contain
    #  less.
    def verify_data_structures(self):
        election_keys = ['election_name', 'contests', 'type']
        contest_keys = ['ident', 'display_name', 'voting_method_id']
        contest_keys += ['open_seat_count', 'candidates', 'district_id']
        candidate_keys = ['count', 'display_name', 'ident', 'party_id']
        for election in self.b1:
            for contest in record:
                for candidate in contest:

    # Helper function for self.verify_data_structures. Verifies that a
    #  dictionary only contains the given list of keys, no more nor less
    def has_only_keys(dict, key_list):
        
    

    # Verify that the data stored in each field of each data structure
    #  is valid data for that field, i.e. vote counts should not be
    #  negative numbers, candidate names must be strings, etc.
    """def verify_fields(self):"""
    
    # This returns true if the data members of two contests have the
    #  same values. Else returns false.
    def match_contest(self, cont1, cont2):
        if (cont1['display_name'] != cont2['display_name']) or \
        (cont1['district_id'] != cont2['district_id']) or \
        (cont1['ident'] != cont2['ident']) or \
        (cont1['open_seat_count'] != cont2['open_seat_count']) or \
        (cont1['voting_method_id'] != cont2['voting_method_id']) or \
        (len(cont1['candidates']) != len(cont2['candidates'])):
            return False
        for i in range(len(cont1['candidates'])):
            if not self.match_candidate(cont1['candidates'][i],
                                        cont2['candidates'][i]):
                return False
        return True

    # This returns true if the data members of two candidates have the
    #  same values (with the exception of count). Else returns false.
    def match_candidate(self, cand1, cand2):
        if((cand1['display_name'] != cand2['display_name']) or
        (cand1['ident'] != cand2['ident']) or
        (cand1['party_id'] != cand2['party_id'])):
            return False
        return True

    # Sums up the separate vote counts in each record for each candidate
    #  and returns the cumulative result as a dictionary.
    def sumation(self):
        sum_dict = {}
        for rec in self.b1:     
            for i in range(len(rec['contests'])):
                for j in range(len(rec['contests'][i]['candidates'])):
                    c_name = rec['contests'][i]['candidates'][j]['display_name']
                    if not sum_dict.has_key(c_name):
                        sum_dict[c_name] = 0                    
                    c_count = rec['contests'][i]['candidates'][j]['count']
                    sum_dict[c_name] += c_count
        for rec in self.b2:
            for i in range(len(rec['contests'])):
                for j in range(len(rec['contests'][i]['candidates'])):
                    c_name = rec['contests'][i]['candidates'][j]['display_name']
                    c_count = rec['contests'][i]['candidates'][j]['count']
                    sum_dict[c_name] += c_count
        return sum_dict

def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 6 ):
        print "Usage: [ELECTION SPECS FILE] [BALLOT RECORD1]",
        print "[BALLOT RECORD2] [MERGED OUTPUT FILE]", 
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
