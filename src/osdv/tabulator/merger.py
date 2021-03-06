#!/usr/bin/env python

"""
Developed with Python 2.6.2
Name: merger.py
Author: Mike Anderson
Created: September 26, 2009
Purpose: To define a class that merges two ballot record files
 together into one file.
"""

from __future__ import with_statement
import yaml
import sys
import uuid

from xml_serializer import xml_serialize
import audit_header

class Merger(object):

    """
    Check validity of two ballot record files and an election spec, and
     generate a report.
    """
    
    def __init__(self, election, record1, record2,
                 merge_output):
        self.rstream = open(''.join([merge_output,'.log']), 'w')
        # Load ballot records from yaml file
        try:
            stream = open(''.join([record1,'.yml']), 'r')
        except IOError:
            self.rstream.write(''.join(['Unable to open ',record1,'\n']))
            print(''.join(['Unable to open ',record1,'\n']))
            raise
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid1 = a.file_id
            prov1 = a.provenance
            self.b1 = list(yaml.load_all(stream))
            stream.close()
        try:
            stream = open(''.join([record2,'.yml']), 'r')
        except IOError:
            self.rstream.write(''.join(['Unable to open ',record2,'\n']))
            print(''.join(['Unable to open ',record2,'\n']))
            raise
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid2 = a.file_id
            prov2 = a.provenance
            self.b2 = list(yaml.load_all(stream))
            stream.close()

        # Get the election specs from file
        try:
            stream = open(''.join([election,'.yml']), 'r')
        except IOError:
            self.rstream.write(''.join(['Unable to open ',record2,'\n']))
            print(''.join(['Unable to open ',record2,'\n']))
            raise
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            self.templ_type = a.type
            self.e = yaml.load(stream)
            stream.close()
            if self.e.has_key('precinct_list'):
                del self.e['precinct_list']

        # Combine provenances and guids from input files
        self.new_prov = []
        self.new_prov.extend(prov1)
        self.new_prov.extend(prov2)
        self.new_prov.append(guid1)
        self.new_prov.append(guid2)

    def validate(self):
        """
        Check to see that all input data is valid, results go to stdout
         and into a log file
        """

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

    def validate_GUIDs(self):
        """
        Verify that each GUID contained in the combined provenance of
         the two input files is unique, as a check against double
         counting.
        """
        
        for guid in self.new_prov:
            if self.new_prov.count(guid) > 1:
                return False
        return True

    def validate_data_structures(self):
        """
        Verify that the three input files all contain data structures
         that are consistent with the BallotInfo specs, a data structure
         should not contain more fields than the specs, nor should it
         contain less.
        """

        pcl_keys = ['display_name', 'contest_list', 'number_of_precincts',
         'registered_voters']
        juris_keys = pcl_keys + ['jurisdiction_display_name']
        bct_keys = pcl_keys + ['vote_type', 'prec_ident']
        templ_contest_keys = ['ident', 'display_name', 'candidates',
         'district_ident']
        contest_keys = templ_contest_keys + \
         ['voting_method_ident', 'uncounted_ballots', 'total_votes']
        templ_candidate_keys = ['display_name', 'ident', 'party_ident']
        candidate_keys = templ_candidate_keys + ['count']
        ub_keys = ['blank_votes', 'over_votes']
        for file in ([self.e], self.b1, self.b2):
            if not isinstance(file, list):
                return False
            for elec in file:
                if file == [self.e]:
                    if self.templ_type == 'jurisdiction_slate':
                        if not self.has_only_keys(elec, juris_keys):
                            return False
                    elif self.templ_type == 'precinct_contestlist':
                        if not self.has_only_keys(elec, pcl_keys):
                            return False
                else:
                    if not self.has_only_keys(elec, bct_keys):
                        return False
                if not isinstance(elec['contest_list'], list):
                    return False
                for contest in elec['contest_list']:
                    if file == [self.e]:
                        if not self.has_only_keys(contest, templ_contest_keys):
                            return False
                    else:
                        if not self.has_only_keys(contest, contest_keys):
                            return False
                        if not self.has_only_keys(contest['uncounted_ballots'],
                         ub_keys):
                            return False
                    if not isinstance(contest['candidates'], list):
                        return False
                    for candidate in contest['candidates']:
                        if file == [self.e]:
                            if not self.has_only_keys(candidate, 
                             templ_candidate_keys):
                                return False
                        else:
                            if not self.has_only_keys(candidate,candidate_keys):
                                return False
        return True

    def has_only_keys(self, d, key_list):        
        """
        Helper function for self.verify_data_structures. Verifies that d
         is a dictionary and it only contains the given list of keys, no
         more nor less.
        """
        
        if not isinstance(d, dict):
            return False
        for k in key_list:
            if not d.has_key(k):
                return False
        if len(d.keys()) != len(key_list):
            return False
        return True

    def validate_fields(self):
        """
        Verify that the data stored in each field of each data structure
         is valid data for that field, i.e. vote counts should not be
         negative numbers, candidate names must be strings, etc.
        """
        
        for file in ([self.e], self.b1, self.b2):
            for election in file:
                if not isinstance(election['display_name'], str):
                    return False
                if file != [self.e]:
                    if not isinstance(election['display_name'], str):
                        return False
                    if not isinstance(election['number_of_precincts'], int):
                        return False
                    if not isinstance(election['prec_ident'], str):
                        return False
                    if not isinstance(election['registered_voters'], int):
                        return False
                    if not isinstance(election['vote_type'], str):
                        return False

                for contest in election['contest_list']:
                    if file != [self.e]:
                        if not isinstance(contest['voting_method_ident'], str):
                            return False
                        if not isinstance(contest['uncounted_ballots']['blank_votes'], int):
                            return False
                        if not isinstance(contest['uncounted_ballots']['over_votes'], int):
                            return False
                        if not isinstance(contest['total_votes'], int):
                            return False
                        if not isinstance(contest['ident'], str):
                            return False
                    if not isinstance(contest['district_ident'], str):
                        return False
                    if not isinstance(contest['display_name'], str): 
                        return False
                    for candidate in contest['candidates']:
                        if file != [self.e]:
                            if not isinstance(candidate['count'], int):
                                return False
                            if not candidate['count'] >= 0:
                                return False
                        if not isinstance(candidate['display_name'], str):
                            return False
                        if not isinstance(candidate['ident'], str):
                            return False
                        if not isinstance(candidate['party_ident'], str):
                            return False
        return True

    def validate_match_election(self):
        """
        Verify that the two ballot record files are consistent with the
         given election
        """

        # Match the values in each record from both record files to the
        #  election specs. If any pair of values do not match, return
        #  false.
        for file in (self.b1, self.b2):
            for b in file:
                if b['display_name'] != self.e['display_name']:
                    return False
                id_list = []
                for elec_cont in self.e['contest_list']:
                    id_list.append(elec_cont['ident'])
                for bal_cont in b['contest_list']:
                    if id_list.count(bal_cont['ident']) == 0:
                        return False
                    else:
                        if not self.match_contest(bal_cont, 
                         self.e['contest_list']
                         [id_list.index(bal_cont['ident'])]):
                            return False
        return True

    def match_contest(self, cont1, cont2):
        """
        This returns true if the data members of two contests have the
         same values. Else returns false.
        """

        if (cont1['display_name'] != cont2['display_name']) or \
        (cont1['district_ident'] != cont2['district_ident']) or \
        (cont1['ident'] != cont2['ident']) or \
        (len(cont1['candidates']) != len(cont2['candidates'])):            
            return False
        for i in range(len(cont1['candidates'])):
            if not self.match_candidate(cont1['candidates'][i],
                                        cont2['candidates'][i]):
                return False
        return True

    def match_candidate(self, cand1, cand2):
        """
        This returns true if the data members of two candidates have the
         same values (with the exception of count). Else returns false.
        """

        if((cand1['display_name'] != cand2['display_name']) or
        (cand1['ident'] != cand2['ident']) or
        (cand1['party_ident'] != cand2['party_ident'])):
            return False
        return True

    def merge(self, merged_output):
        """
        # Concatenate the two input files together along with a generated
        #  audit header. Dump the result in yaml and xml formats
        """

        # Create an audit header
        a = audit_header.AuditHeader()
        a.set_fields('tabulator_aggregation',
                     'Pito Salas', 'TTV Tabulator TAB02', 
                     'TTV Tabulator 0.1 JUL-1-2008', self.new_prov)

        # Dump merge into a file in yaml format
        with open(''.join([merged_output,'.yml']), 'w') as stream:
            stream.write(a.serialize_yaml())
            yaml.dump_all(self.b1, stream)
            stream.write('---\n')
            yaml.dump_all(self.b2, stream)

        # Dump merge into a file in xml format        
        with open(''.join([merged_output,'.xml']), 'w') as stream:
            stream.write(a.serialize_xml())
            for file in (self.b1, self.b2):
                for record in file:
                    stream.writelines(xml_serialize(record, 0))

def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 5 ):
        print "Usage: [ELECTION SPECS FILE] [BALLOT RECORD FILE 1]",
        print "[BALLOT RECORD FILE 2] [MERGED OUTPUT FILE]"
        return 0

    m = Merger(*sys.argv[1:])
    if m.validate() == False:
        return 0
    m.merge(sys.argv[4])

    with open(''.join([sys.argv[4],'.log']), 'a') as strm:
        print 'Successfully merged %s and %s' % (sys.argv[2],sys.argv[3]),
        strm.write('Successfully merged %s and %s' % (sys.argv[2],sys.argv[3]))
        print 'together\nThe result is stored in %s.yml' % sys.argv[4]
        strm.write('together\nThe result is stored in %s.yml' % sys.argv[4])
        print 'and %s.xml' % sys.argv[4]
        strm.write('and %s.xml\n' % sys.argv[4])
        print 'A log for this run was created in %s.log' % sys.argv[4]

    return 0

if __name__ == '__main__': main()
