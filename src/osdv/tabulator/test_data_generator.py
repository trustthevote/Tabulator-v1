#!/usr/bin/env python
# Python 2.6.2
# Name: test_data_generator.py
# Author: Mike Anderson
# Created: Jul 30, 2009
# Purpose: To generate test files for the ballot tabulator

import random
import yaml
import sys
import copy
import uuid
from plistlib import writePlistToString as xmlSerialize

import audit_header

# Provide random election specs or random ballot counts
class ProvideRandomBallots(object):
    # Takes as its arguments the type of random data to generate
    def __init__(self, type, args):
        # These variables are used to ensure that if the same random
        #  data is generated in some circumstances, it will not appear
        #  twice in the template.
        self.already_used_streps = []
        self.already_used_dreps = []
        self.already_used_names = []
        self.already_used_cand_idents = []
        self.already_used_supreme = False
        self.fname_list = []
        self.lname_list = []

        
        if type == 'election':
        # Generate a sample election and output it to the location
        #  specified by the user in the command line, in yaml and xml
        #  formats.
            b = {}

            # Load a list of first and last names from file
            stream = open('first_names', 'r')
            self.fnames = stream.readlines()
            stream = open('last_names', 'r')
            self.lnames = stream.readlines()

            # Give each file its own audit header, generate data
            a = audit_header.AuditHeader()
            a.set_fields('jurisdiction_slate',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 1.2 JUL-1-2008', [])
            b = self.random_elec()
            b['type'] = 'jurisdiction_slate'
            
            # Dump output into a file in yaml format
            stream = open(args[0] + '.yaml', 'w') 
            stream.write(a.serialize_yaml())
            yaml.dump(b, stream)
            
            # Dump output into a file in XML file
            stream = open(args[0] + '.xml', 'w')
            stream.write(a.serialize_xml())
            stream.writelines(xmlSerialize(b)[173:]. \
                replace('\t', '    ').replace('\n</plist>', ''))

            
        elif type == 'counts':
            # Load election specs from given file in yaml format     
            stream = open(args[1] + '.yaml', 'r')
            for i in range(0,8):  # Ignore the audit header
                stream.readline()
            e = yaml.load(stream)
            e['type'] = 'ballot_counter_total'
        
            # Make the number of random ballot_info records specified by
            #  the user. Use the loaded election specs as a template,
            #  assign the vote counts of each candidate a value between 
            #  0 and 99.
            b_list = []
            for i in range(0, int(args[0])):
                b = copy.deepcopy(e)                
                for j in range(0, len(b['contests'])):
                    for k in range(0, len(b['contests'][j]['candidates'])):
                        r = random.randint(0,99)
                        b['contests'][j]['candidates'][k]['count'] = r
                b_list.append(b)
            
            # Give each file its own audit header            
            a = audit_header.AuditHeader()
            a.set_fields('ballot_counter_total',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 1.2 JUL-1-2008', [])

            # Dump output into a file in yaml format
            stream = open(args[2] + '.yaml', 'w')
            stream.write(a.serialize_yaml())
            yaml.dump_all(b_list, stream)

            # Dump output into a file in XML file
            stream = open(args[2] + '.xml', 'w')
            stream.write(a.serialize_xml())
            for record in b_list:
                stream.writelines(xmlSerialize(record)[173:]. \
                    replace('\t', '    ').replace('\n</plist>', ''))


        else:
            exit()
    
    # Make and returns a ballot with initialized data members
    def random_elec(self):        
        self.cand_num = 1
                
        b = {}
        
        # Make the election headliner some random presidential election
        r = random.randint(0,3)
        b['election_name'] = str(r*4+2000) + " Presidential"
        
        # Generate a few contests
        b['contests'] = []
        r = random.randint(2,5)
        for i in range(0,r):
            b['contests'].append(self.random_contest())            
        return b

    # Make and returns a contest object with initialized data members
    def random_contest(self):
        cont = {}

        # Generate a few candidates per contest
        cont['candidates'] = []
        r = random.randint(3,5)
        for i in range(0,r):            
            cont['candidates'].append(self.random_candidate())
        
        # Make sure that a maximum of one supreme court justice contest
        #  is generated.
        if self.already_used_supreme:
            r = random.randint(1,2)
        else:
            r = random.randint(1,3)
        
        # Generate a random type of race
        if r == 1:
            cont['display_name'] = 'Representative in Congress'

            # Generate random values for the dist number until an unused
            #  number is generated. Once this is successful, use the
            #  unused number and add it to a list of used numbers.
            while True:
                r = random.randint(1,9)
                if self.already_used_dreps.count(r) == 0:
                    self.already_used_dreps.append(r)
                    if r == 1:
                        cont['ident'] = 'Rep1stDistrict'
                    elif r == 2:
                        cont['ident'] = 'Rep2ndDistrict'
                    elif r == 3:
                        cont['ident'] = 'Rep3rdDistrict'
                    else:
                        cont['ident'] = 'Rep'+str(r)+'thDistrict'
                    break
        elif r == 2:
            cont['display_name'] = 'State Representative'
            
            # Generate random values for the House number until an
            #  unused number is generated. Once this is successful, use
            #  the unused number and add it to a list of used numbers.
            while True:
                r = random.randint(1,9)
                if self.already_used_streps.count(r) == 0:
                    self.already_used_streps.append(r)
                    if r == 1:
                        cont['ident'] = 'StateRep1stHouse'
                    elif r == 2:
                        cont['ident'] = 'StateRep2ndHouse'
                    elif r == 3:
                        cont['ident'] = 'StateRep3rdHouse'
                    else:
                        cont['ident'] = 'StateRep'+str(r)+'thHouse'
                    break
        else:
            cont['display_name'] = 'Supreme Court Justice'
            cont['ident'] = 'JustSupCrt'
            self.already_used_supreme = True
    
        r = random.randint(1,2)
        cont['open_seat_count'] = r
        
        # The district number and the voting machine number are 
        #  randomly generated.
        r = random.randint(0,6)
        if r == 0:
            cont['district_id'] = "PRES"
        if r == 1:
            r2 = random.randint(1,10)
            cont['district_id'] = 'USREP ' + str(r2)
        if r == 2:
            r2 = random.randint(1,10)
            cont['district_id'] = 'HOUSE ' + str(r2)
        if r == 3:
            r2 = random.randint(1,10)
            cont['district_id'] = 'SENATE ' + str(r2)
        if r == 4:
            cont['district_id'] = 'SOILWATER'
        if r == 5:
            cont['district_id'] = 'HARBOR'       
        if r == 6:
            r2 = random.randint(1,5)
            cont['district_id'] = 'SCHOOL ' + str(r2)

        cont['voting_method_id'] = 'VOTM-' + str(random.randint(1,5))
        return cont

    # Make and returns a candidate object with initialized data members
    def random_candidate(self):
        cand = {}
        
        # Count just gets a null value, since it is irrelevant to the
        #  specs generated here.
        cand['count'] = 0
        
        cand['display_name'] = self.random_fullname()
        while True:
            r = random.randint(100,999)
            if self.already_used_cand_idents.count(r) == 0:
                self.already_used_cand_idents.append(r)
                cand['ident'] = 'CAND-' + str(r)
                break           
        cand['party_id'] = 'PART-' + str(random.randint(1,9))
        
        return cand
    
    # Make and returns a random full name string
    def random_fullname(self):
        # Generate a first and last name combination
        fname = self.fnames[random.randint(0, len(self.fnames) - 1)].strip()
        lname = self.lnames[random.randint(0, len(self.lnames) - 1)].strip()
        fullname = fname + ' ' + lname
        
        if self.already_used_names.count(fullname) == 0:
            self.already_used_names.append(fullname)
            return fullname
        else:
            return(self.random_fullname())      

def main(): 
    # First make sure that the command line input is valid. If it is not
    #  then output a usage statement and exit    
    if len(sys.argv) == 1: sys.argv.append("")
    type = sys.argv[1]
    if sys.argv[1] == "election":
        if len(sys.argv) != 3:
            print "Usage: test_data_generator.py election [OUTPUT ELECTION FILE]"
            print "   OR: test_data_generator.py counts [#  OF SAMPLES]",
            print "[INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]"
            exit()
    elif sys.argv[1] == "counts":
        if len(sys.argv) != 5:
            print "Usage: test_data_generator.py election [OUTPUT ELECTION FILE]"
            print "   OR: test_data_generator.py counts [#  OF SAMPLES]",
            print "[INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]"
            exit()
    else:
        print "Usage: test_data_generator.py election [OUTPUT ELECTION FILE]"
        print "   OR: test_data_generator.py counts [#  OF SAMPLES]",
        print "[INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]"
        exit()
    
    # Get rid of unneccesary command line arguments and generate random
    #  data of the specified type
    args = sys.argv[2:]
    p = ProvideRandomBallots(type, args)
    
    if sys.argv[1] == "election":
        print "Done. Generated sample election template files",
        print sys.argv[2] + ".yaml and " + sys.argv[2] + ".xml \n"
    else:
        print "Done. Generated sample ballot files",
        print sys.argv[4] + ".yaml and " + sys.argv[4] + ".xml \n"

    return 0
    
if __name__ == '__main__': main()
