#!/usr/bin/env python
# Python 2.6.2
# Name: merger.py
# Author: Mike Anderson
# Created: September 26, 2009
# Purpose: To define a class that merges two ballot record files
#  together into one file.

import yaml
import sys
import uuid
from plistlib import writePlistToString as xmlSerialize

import audit_header

# Check validity of two ballot record files and an election spec, and
#  generate a report.
class Merger(object):
    def __init__(self, election, record1, record2,
                 merge_output):
        # Load ballot records from yaml file
        try:
            stream = open(record1 + '.yaml', 'r')
        except:
            self.rstream.write('Unable to open ' + record1 + '\n')
            print('Unable to open ' + record1 + '\n')
            exit(0)
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid1 = a.file_id
            prov1 = a.provenance
            self.b1 = list(yaml.load_all(stream))
        try:
            stream = open(record2 + '.yaml', 'r')
        except:
            self.rstream.write('Unable to open ' + record2 + '\n')
            print('Unable to open ' + record2 + '\n')
            exit(0)
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid2 = a.file_id
            prov2 = a.provenance
            self.b2 = list(yaml.load_all(stream))

        # Get the election specs from file
        stream = open(election + '.yaml', 'r')
        for i in range(0,8):  # Ignore the audit header
            stream.readline()
        self.e = yaml.load(stream)
        stream.close()

        # Combine provenances and guids from input ballot_counter_total
        #  files
        self.new_prov = []
        self.new_prov.extend(prov1)
        self.new_prov.extend(prov2)
        self.new_prov.append(guid1)
        self.new_prov.append(guid2)        

    # Check to see that all input data is valid, results go to stdout
    #  and into a log file
    def validate(self, fname):        
        strm = open(fname, 'w')
        print "Data validation results:"
        strm.write("Data validation results:\n")

        print " Are all GUIDs unique ...",
        strm.write(" Are all GUIDs unique ... ")
        if self.validate_GUIDs():
            print "Yes"
            strm.write("Yes\n")
        else:
            print " No, merge aborted"
            strm.write(" No, merge aborted\n")
            return False

        print " Do input files contain BallotInfo data structures ...",
        strm.write(" Do input files contain BallotInfo data structures ... ")
        if self.validate_data_structures():
            print "Yes"
            strm.write("Yes\n")
        else:
            print " No, merge aborted"
            strm.write(" No, merge aborted\n")
            return False

        print " Do all fields contain good values of the proper type ...",
        strm.write(" Do all fields contain good values of the proper type ... ")
        if self.validate_fields():
            print "Yes"
            strm.write("Yes\n")
        else:
            print "No, merge aborted"
            strm.write("No, merge aborted\n")
            return False

        print " Do both record files match the given election ...",
        strm.write(" Do both record files match the given election ... ")
        if self.validate_match_election():
            print "Yes"
            strm.write("Yes\n")
        else:
            print "No, merge aborted"
            strm.write("No, merge aborted\n")
            return False

        print "All validation tests passed\n"
        strm.write("All validation tests passed\n")
        strm.close()        
        return True

    # Verify that each GUID contained in the combined provenance of the
    #  two ballot-counter-total input files is unique, as a check
    #  against double counting.  
    def validate_GUIDs(self):
        for guid in self.new_prov:
            if self.new_prov.count(guid) > 1:
                return False
        return True

    # Verify that the three input files all contain data structures that
    #  are consistent with the BallotInfo specs, a data structure should
    #  not contain more fields than the specs, nor should it contain
    #  less.
    def validate_data_structures(self):
        election_keys = ['election_name', 'contests', 'type']
        contest_keys = ['ident', 'display_name', 'voting_method_id']
        contest_keys += ['open_seat_count', 'candidates', 'district_id']
        candidate_keys = ['count', 'display_name', 'ident', 'party_id']
        for file in ([self.e], self.b1, self.b2):            
            if type(file) != list:
                return False
            for election in file:
                if not self.has_only_keys(election, election_keys):
                    return False                
                if type(election['contests']) != list:
                    return False
                for contest in election['contests']:
                    if not self.has_only_keys(contest, contest_keys):
                        return False
                    if type(contest['candidates']) != list:
                        return False
                    for candidate in contest['candidates']:
                        if not self.has_only_keys(candidate, candidate_keys):
                            return False
        return True

    # Helper function for self.verify_data_structures. Verifies that d
    #  is a dictionary and it only contains the given list of keys, no
    #  more nor less.
    def has_only_keys(self, d, key_list):        
        if not type(d) == dict:
            return False
        for k in key_list:
            if not d.has_key(k):
                return False
        if len(d.keys()) != len(key_list):
            return False
        return True

    # Verify that the data stored in each field of each data structure
    #  is valid data for that field, i.e. vote counts should not be
    #  negative numbers, candidate names must be strings, etc.
    def validate_fields(self):
        for file in ([self.e], self.b1, self.b2):
            for election in file:
                if type(election['election_name']) != str:                    
                    return False
                if election['type'] != 'precinct_contestlist' and \
                   election['type'] != 'ballot_counter_total' and \
                   election['type'] != 'tabulator_aggregation':
                    return False
                for contest in election['contests']:
                    if type(contest['ident']) != str:
                        return False
                    if type(contest['display_name']) != str:
                        return False
                    if type(contest['voting_method_id']) != str:
                        return False
                    if type(contest['open_seat_count']) != int:
                        return False
                    if not contest['open_seat_count'] >= 1:
                        return False
                    if type(contest['district_id']) != str:
                        return False
                    for candidate in contest['candidates']:
                        if type(candidate['count']) != int:
                            return False
                        if not candidate['count'] >= 0:
                            return False
                        if type(candidate['display_name']) != str:
                            return False
                        if type(candidate['ident']) != str:
                            return False
                        if type(candidate['party_id']) != str:
                            return False
        return True
  
    # Verify that the two ballot record files are consistent with the
    #  given election
    def validate_match_election(self):
        # Match the values in each record from both record files to the
        #  election specs. If any pair of values do not match, return
        #  false.
        for file in (self.b1, self.b2):
            for b in file:
                if ((b['election_name'] != self.e['election_name']) or \
                (len(b['contests']) != len(self.e['contests']))):
                    return False
                for i in range(len(self.e['contests'])):
                    if not self.match_contest(self.e['contests'][i],
                                              b['contests'][i]):
                        return False
        return True

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

    # Concatenate the two input files together along with a generated
    #  audit header. Dump the result in yaml and xml formats
    def merge(self, merged_output):
        # Create an audit header
        a = audit_header.AuditHeader()
        a.set_fields('tabulator_aggregation',
                     'Pito Salas', 'TTV Tabulator TAB02', 
                     'TTV Tabulator 1.2 JUL-1-2008', self.new_prov)

        # Dump merge into a file in yaml format
        stream = open(merged_output + '.yaml', 'w')
        stream.write(a.serialize_yaml())
        yaml.dump_all(self.b1, stream)
        stream.write('---\n')
        yaml.dump_all(self.b2, stream)

        # Dump merge into a file in xml format        
        stream = open(merged_output + '.xml', 'w')
        stream.write(a.serialize_xml())
        for file in (self.b1, self.b2):
            for record in file:
                stream.writelines(xmlSerialize(record)[173:]. \
                    replace('\t', '    ').replace('\n</plist>', ''))
        stream.close()

def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 5 ):
        print "Usage: [ELECTION SPECS FILE] [BALLOT RECORD FILE 1]",
        print "[BALLOT RECORD FILE 2] [MERGED OUTPUT FILE]"
        return 0

    m = Merger(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    if m.validate(sys_argv[4] + ".log") == False:
        return 0
    m.merge(sys_argv[4])
        
    strm = open(sys.argv[4] + '.log', 'a')
    print "Successfully merged " + sys.argv[2] + " and " + sys.argv[3],
    strm.write("Successfully merged " + sys.argv[2] + " and " + sys.argv[3])
    print "together\nThe result is stored in " + sys.argv[4] + ".yaml",
    strm.write(" together\nThe result is stored in " + sys.argv[4] + ".yaml")
    print "and " + sys.argv[4] + ".xml"
    strm.write(" and " + sys.argv[4] + ".xml\n")
    print "An error log was created in " + sys.argv[4] + ".log"

    return 0

if __name__ == '__main__': main()
