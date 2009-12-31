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

import tabulator_source.audit_header as audit_header

# Check validity of two ballot record files and an election spec, and
#  generate a report.
class Merger(object):
    def __init__(self, election, record1, record2,
                 merge_output):
        self.rstream = open(merge_output + '.log', 'w')
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
            stream.close()
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
            stream.close()

        # Get the election specs from file
        with open(election + '.yaml', 'r') as stream:
            for i in range(0,8):  # Ignore the audit header
                stream.readline()
            self.e = yaml.load(stream)
            if self.e.has_key('precinct_list'):
                del self.e['precinct_list']

        # Combine provenances and guids from input files
        self.new_prov = []
        self.new_prov.extend(prov1)
        self.new_prov.extend(prov2)
        self.new_prov.append(guid1)
        self.new_prov.append(guid2)

    # Check to see that all input data is valid, results go to stdout
    #  and into a log file
    def validate(self):
        print "Data validation results:"
        self.rstream.write("Data validation results:\n")

        print " Check 1: Check that GUIDs are unique => ",
        self.rstream.write(" Check 1: Check that GUIDs are unique => ")
        if self.validate_GUIDs():
            print "SUCCEEDED"
            self.rstream.write("SUCCEEDED\n")
        else:
            print "FAILED\nMerge aborted"
            self.rstream.write("FAILED\nMerge aborted\n")
            return False

        print " Check 2: Check that input files contain BallotInfo data structures => ",
        self.rstream.write(" Check 2: Check that input files contain BallotInfo data structures => ")
        if self.validate_data_structures():
            print "SUCCEEDED"
            self.rstream.write("SUCCEEDED\n")
        else:
            print "FAILED\nMerge aborted"
            self.rstream.write("FAILED\nMerge aborted\n")
            return False

        print " Check 3: Check that all fields contain values of the proper type => ",
        self.rstream.write(" Check 3: Check that all fields contain values of the proper type => ")
        if self.validate_fields():
            print "SUCCEEDED"
            self.rstream.write("SUCCEEDED\n")
        else:
            print "FAILED\nMerge aborted"
            self.rstream.write("FAILED\nMerge aborted\n")
            return False

        print " Check 4: Check that both record files match the given election => ",
        self.rstream.write(" Check 4: Check that both record files match the given election => ")
        if self.validate_match_election():
            print "SUCCEEDED"
            self.rstream.write("SUCCEEDED\n")
        else:
            print "FAILED"
            self.rstream.write("FAILED\n")
            return False

        print "All validation tests passed\n"
        self.rstream.write("All validation tests passed\n")
        self.rstream.close()        
        return True

    # Verify that each GUID contained in the combined provenance of the
    #  two input files is unique, as a check against double counting.  
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
        election_keys = ['election_name', 'contests', 'type', 'vote_type',
         'prec_id', 'number_of_precincts', 'registered_voters']
        templ_contest_keys = ['contest_id', 'display_name', 'candidates', 'district_id']
        bct_contest_keys = ['contest_id', 'display_name', 'voting_method_id',
         'candidates', 'district_id', 'uncounted_ballots', 'total_votes']
        candidate_keys = ['count', 'display_name', 'ident', 'party_id']
        ub_keys = ['blank_votes', 'over_votes']
        for file in ([self.e], self.b1, self.b2):
            if not isinstance(file, list):
                return False
            for elec in file:
                if not self.has_only_keys(elec, election_keys):
                    return False                
                if not isinstance(elec['contests'], list):
                    return False
                for contest in elec['contests']:
                    if file == [self.e]:
                        if not self.has_only_keys(contest, templ_contest_keys):
                            return False
                    else:
                        if not self.has_only_keys(contest, bct_contest_keys):
                            return False
                        if not self.has_only_keys(contest['uncounted_ballots'],
                         ub_keys):
                            return False
                    if not isinstance(contest['candidates'], list):
                        return False
                    for candidate in contest['candidates']:
                        if not self.has_only_keys(candidate, candidate_keys):
                            return False
        return True

    # Helper function for self.verify_data_structures. Verifies that d
    #  is a dictionary and it only contains the given list of keys, no
    #  more nor less.
    def has_only_keys(self, d, key_list):        
        if not isinstance(d, dict):
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
                if not isinstance(election['election_name'], str):
                    return False
                if file == [self.e]:
                    if election['type'] != 'precinct_contestlist' and \
                       election['type'] != 'jurisdiction_slate':                        
                        return False
                else:
                    if election['type'] != 'ballot_counter_total' and \
                     election['type'] != 'tabulator_aggregation':                        
                        return False
                    if not isinstance(election['election_name'], str):
                        return False
                    if not isinstance(election['number_of_precincts'], int):
                        return False
                    if not isinstance(election['prec_id'], str):
                        return False
                    if not isinstance(election['registered_voters'], int):
                        return False
                    if not isinstance(election['vote_type'], str):
                        return False

                for contest in election['contests']:
                    if file != [self.e]:
                        if not isinstance(contest['voting_method_id'], str):
                            return False
                        if not isinstance(contest['uncounted_ballots']['blank_votes'], int):
                            return False
                        if not isinstance(contest['uncounted_ballots']['over_votes'], int):
                            return False
                        if not isinstance(contest['total_votes'], int):
                            return False
                        if not isinstance(contest['contest_id'], str):
                            return False
                    if not isinstance(contest['district_id'], str):
                        return False
                    if not isinstance(contest['display_name'], str): 
                        return False
                    for candidate in contest['candidates']:
                        if not isinstance(candidate['count'], int):
                            return False
                        if not candidate['count'] >= 0:
                            return False
                        if not isinstance(candidate['display_name'], str):
                            return False
                        if not isinstance(candidate['ident'], str):
                            return False
                        if not isinstance(candidate['party_id'], str):
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
                if b['election_name'] != self.e['election_name']:
                    return False
                id_list = []
                for elec_cont in self.e['contests']:
                    id_list.append(elec_cont['contest_id'])
                for bal_cont in b['contests']:
                    if id_list.count(bal_cont['contest_id']) == 0:
                        return False
                    else:
                        if not self.match_contest(bal_cont, self.e['contests'] \
                         [id_list.index(bal_cont['contest_id'])]):
                             return False
        return True

    # This returns true if the data members of two contests have the
    #  same values. Else returns false.
    def match_contest(self, cont1, cont2):
        if (cont1['display_name'] != cont2['display_name']) or \
        (cont1['district_id'] != cont2['district_id']) or \
        (cont1['contest_id'] != cont2['contest_id']) or \
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
                     'TTV Tabulator 0.1 JUL-1-2008', self.new_prov)

        # Dump merge into a file in yaml format
        with open(merged_output + '.yaml', 'w') as stream:
            stream.write(a.serialize_yaml())
            yaml.dump_all(self.b1, stream)
            stream.write('---\n')
            yaml.dump_all(self.b2, stream)

        # Dump merge into a file in xml format        
        with open(merged_output + '.xml', 'w') as stream:
            stream.write(a.serialize_xml())
            for file in (self.b1, self.b2):
                for record in file:
                    stream.writelines(xmlSerialize(record)[173:]. \
                        replace('\t', '    ').replace('\n</plist>', ''))

def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 5 ):
        print "Usage: [ELECTION SPECS FILE] [BALLOT RECORD FILE 1]",
        print "[BALLOT RECORD FILE 2] [MERGED OUTPUT FILE]"
        return 0

    m = Merger(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    if m.validate() == False:
        return 0
    m.merge(sys.argv[4])

    with open(sys.argv[4] + '.log', 'a') as strm:
        print "Successfully merged " + sys.argv[2] + " and " + sys.argv[3],
        strm.write("Successfully merged " + sys.argv[2] + " and " + sys.argv[3])
        print "together\nThe result is stored in " + sys.argv[4] + ".yaml",
        strm.write(" together\nThe result is stored in " + sys.argv[4] + ".yaml")
        print "and " + sys.argv[4] + ".xml"
        strm.write(" and " + sys.argv[4] + ".xml\n")
        print "A log for this run was created in " + sys.argv[4] + ".log"

    return 0

if __name__ == '__main__': main()
