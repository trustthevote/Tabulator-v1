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

import audit_header

# Checks validity of two ballot record files against some election
#  specs, merges them together, and generates a report.
class Tabulator(object):
    def __init__(self, election_file, record_file1, record_file2,
                 merge_output_file, report_output_file):
        # Open a stream to a report file that will be written to during
        #  the course of tabulation.
        self.rstream = open(report_output_file, 'w')
        
        # Load ballot records from file
        try:
            stream = open(record_file1, 'r')
        except:
            self.rstream.write('Unable to open ' + record_file1 + '\n')
            print('Unable to open ' + record_file1 + '\n')
            exit()
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid1 = a.file_id
            prov1 = a.provenance
            
            self.b1 = []
            self.b1 = yaml.load_all(stream)        
        try:
            stream = open(record_file2, 'r')
        except:
            self.rstream.write('Unable to open ' + record_file2 + '\n')
            print('Unable to open ' + record_file2 + '\n')
            exit()
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            guid2 = a.file_id
            prov2 = a.provenance
            
            self.b2 = []
            self.b2 = yaml.load_all(stream)
        
        # Get the election specs from file
        stream = open(election_file, 'r')
        for i in range(0,8):  # Ignore the audit header
            stream.readline()
        self.e = yaml.load(stream)
            
        # Verify that ballot records match the election specs in file
        self.verify_match_record(election_file)
                
        # Generators were already iterated over by verify_match_record,
        #  so reload.
        stream = open(record_file1, 'r')
        for i in range(0,8):  # Ignore the audit header
            stream.readline()
        self.b1 = yaml.load_all(stream)
        stream = open(record_file2, 'r')
        for i in range(0,8):  # Ignore the audit header
            stream.readline()
        self.b2 = yaml.load_all(stream)
        
        stream = open(merge_output_file, 'w')    
        
        # Combine provenances and guids from input files
        new_prov = []
        new_prov.extend(prov1)
        new_prov.extend(prov2)
        new_prov.append(guid1)
        new_prov.append(guid2)        
        
        # If the same GUID appears twice, then abort the merge
        for guid in new_prov:
            if new_prov.count(guid) > 1:
                print "Input files contain the same ballot record, merge aborted\n"
                self.rstream.write("Input files contain the same ballot record, merge aborted\n")
                exit()          
        
        a = audit_header.AuditHeader()
        a.set_fields('precinct_contestlist',
                     'Pito Salas', 'TTV Tabulator TAB02', 
                     'TTV Tabulator 1.2 JUL-1-2008', new_prov)
        stream.write(a.serialize())        

        # Add the vote counts of candidates with the same ID# using
        #  merge(). Write the vote totals for each candidate to the
        #  report stream.
        m = self.merge()
        self.rstream.write('\n')
        for i in range(len(m['contest_list'])):
            for j in range(len(m['contest_list'][i]['candidate_list'])):
                tot = m['contest_list'][i]['candidate_list'][j]['count'][0]
                name = m['contest_list'][i]['candidate_list'][j]['display_name']
                self.rstream.write(str(tot) + ' votes found for ' + name + '\n')

        # Generators were already iterated over by merge, so reload.
        read_stream = open(record_file1, 'r')
        for i in range(0,8):  # Ignore the audit header
            read_stream.readline()
        self.b1 = yaml.load_all(read_stream)
        read_stream = open(record_file2, 'r')
        for i in range(0,8):  # Ignore the audit header
            read_stream.readline()
        self.b2 = yaml.load_all(read_stream)

        # Concatenate the two input files, minus their headers, into the
        #  output file.
        yaml.dump_all(self.b1, stream)
        stream.write('---\n')
        yaml.dump_all(self.b2, stream)
                
        stream.close()
        self.rstream.close()
        
    # This function is used to make sure that records in both files are 
    #  consistent with the given election specs.
    def verify_match_record(self, election_file):
        # Match the values in each record from both record files to the
        #  election specs. If any pair of values do not match, return
        #  the number (1 or 2) of the offending record file. Otherwise
        #  return 0
        for b in self.b1:
            if ((b['election_name'] != self.e['election_name']) or
            (len(b['contest_list']) != len(self.e['contest_list']))):             
                print "First record file did not match election template, merge aborted\n"
                self.rstream.write("First record file did not match election template, merge aborted\n")
                exit()
            for i in range(len(self.e['contest_list'])):
                if not self.match_contest(self.e['contest_list'][i],
                                          b['contest_list'][i]):
                    print "First record file did not match election template, merge aborted\n"
                    self.rstream.write("First record file did not match election template, merge aborted\n")
                    exit()
        for b in self.b2:
            if (b['election_name'] != self.e['election_name']) or \
            (len(b['contest_list']) != len(self.e['contest_list'])):
                print "Second record file did not match election template, merge aborted\n"
                self.rstream.write("Second record file did not match election template, merge aborted\n")
                exit()
            for i in range(len(self.e['contest_list'])):
                if not self.match_contest(self.e['contest_list'][i], 
                                          b['contest_list'][i]):
                    print "Second record file did not match election template, merge aborted\n"
                    self.rstream.write("Second record file did not match election template, merge aborted\n")
                    exit()
        self.rstream.write("Both record files matched election template.\n")
                
    # This returns true if the data members of two contests have the
    #  same values. Else returns false.
    def match_contest(self, cont1, cont2):
        if (cont1['display_name'] != cont2['display_name']) or \
        (cont1['district_id'] != cont2['district_id']) or \
        (cont1['ident'] != cont2['ident']) or \
        (cont1['open_seat_count'] != cont2['open_seat_count']) or \
        (cont1['voting_method_id'] != cont2['voting_method_id']) or \
        (len(cont1['candidate_list']) != len(cont2['candidate_list'])):
            return False
        for i in range(len(cont1['candidate_list'])):
            if not self.match_candidate(cont1['candidate_list'][i],
                                        cont2['candidate_list'][i]):
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
    #  and returns the cumulative result as a ballot_info object.
    def merge(self):
        merge = self.e        #  Vote counts of each candidate are 0 in e
        for rec in self.b1:     
            for i in range(len(rec['contest_list'])):
                for j in range(len(rec['contest_list'][i]['candidate_list'])):
                    cur_tot = merge['contest_list'][i]['candidate_list'][j]['count'][0]
                    add_this = rec['contest_list'][i]['candidate_list'][j]['count'][0]
                    sum = cur_tot + add_this      
                    merge['contest_list'][i]['candidate_list'][j]['count'] = [sum]
        for rec in self.b2:
            for i in range(len(rec['contest_list'])):
                for j in range(len(rec['contest_list'][i]['candidate_list'])):
                    cur_tot = merge['contest_list'][i]['candidate_list'][j]['count'][0]
                    add_this = rec['contest_list'][i]['candidate_list'][j]['count'][0]
                    sum = cur_tot + add_this
                    merge['contest_list'][i]['candidate_list'][j]['count'] = [sum]
        return merge            

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
    print "together\n The result is stored in " + sys.argv[4]
    print "A report describing attributes of the merge was created",
    print "in " + sys.argv[5]   
    
    return 0
    
if __name__ == '__main__': main()
