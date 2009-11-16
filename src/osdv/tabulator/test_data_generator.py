#!/usr/bin/env python
# Python 2.6.2
# Name: test_data_generator.py
# Author: Mike Anderson
# Created: Jul 30, 2009
# Purpose: To generate test data files for the merger and tabulator

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
    def __init__(self, args):
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

        self.type = args[0]
        if self.type == 'jurisdiction':
        # Generate a sample jurisdiction_slate and output it to the
        #  location specified by the user in the command line, in yaml
        #  and xml formats.
            b = {}

            # Give each file its own audit header, generate data
            a = audit_header.AuditHeader()
            a.set_fields('jurisdiction_slate',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 0.1 JUL-1-2008', [])
            b = self.make_juris()
            b['type'] = 'jurisdiction_slate'

            # Dump output into a file in yaml format
            stream = open(args[1] + '.yaml', 'w') 
            stream.write(a.serialize_yaml())
            yaml.dump(b, stream)
            
            # Dump output into a file in XML file
            stream = open(args[1] + '.xml', 'w')
            stream.write(a.serialize_xml())
            stream.writelines(xmlSerialize(b)[173:]. \
                replace('\t', '    ').replace('\n</plist>', ''))

        elif self.type == 'contestlist':
        # Generate a sample election and output it to the location
        #  specified by the user in the command line, in yaml and xml
        #  formats.
            b = {}

            # Give each file its own audit header, generate data
            a = audit_header.AuditHeader()
            a.set_fields('precinct_contestlist',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 0.1 JUL-1-2008', [])
            b = self.random_elec()
            b['type'] = 'precinct_contestlist'

            # Dump output into a file in yaml format
            stream = open(args[1] + '.yaml', 'w') 
            stream.write(a.serialize_yaml())
            yaml.dump(b, stream)
            
            # Dump output into a file in XML file
            stream = open(args[1] + '.xml', 'w')
            stream.write(a.serialize_xml())
            stream.writelines(xmlSerialize(b)[173:]. \
                replace('\t', '    ').replace('\n</plist>', ''))

        elif self.type == 'counts':
            # Load election specs from given file in yaml format            
            stream = open(args[2] + '.yaml', 'r')
            for i in range(0,8):  # Ignore the audit header
                stream.readline()
            e = yaml.load(stream)

            # Make the number of random ballot_info records specified by
            #  the user. Use the loaded election specs as a template,
            #  assign the vote counts of each candidate a value between 
            #  0 and 99.
            b_list = []
            for i in range(int(args[1])):
                b = {}
                for key in e.keys():
                    if key != 'contests' and key != 'precinct_list':
                        b[key] = e[key]
                b['contests'] = []
                b['type'] = 'ballot_counter_total'
                b['prec_id'] = 'PREC-' + str(random.randint(1,8))
                for j in range(len(e['contests'])):
                    # If the template was a jurisdiction_slate, then
                    #  do not include contests that were not generated
                    #  in a district in this precinct.
                    if e.has_key('precinct_list'):
                        valid_contest = False
                        for prec in e['precinct_list']:
                            if prec['prec_id'] == b['prec_id']:
                                for dist in prec['districts']:
                                    if dist['ident'] == \
                                     e['contests'][j]['district_id']:
                                        valid_contest = True
                                        break
                        if not valid_contest:
                            continue
                    b['contests'].append(copy.deepcopy(e['contests'][j]))
                    for cand in b['contests'][-1]['candidates']:
                        cand['count'] = random.randint(1,99)
                        b['contests'][-1]['total_votes'] += cand['count']
                    b['contests'][-1]['uncounted_ballots']['blank_votes'] = \
                     random.randint(1,10)
                    b['contests'][-1]['uncounted_ballots']['over_votes'] = \
                     random.randint(1,10)

                # Generate a random polling type for this session
                r = random.randint(0,3)
                if r == 0:
                    b['vote_type'] = 'Polling'
                elif r == 1:
                    b['vote_type'] = 'Early Voting'
                elif r == 2:
                    b['vote_type'] = 'Absentee'
                else:
                    b['vote_type'] = 'Other'

                b_list.append(b)

            # Give each file its own audit header
            a = audit_header.AuditHeader()
            a.set_fields('ballot_counter_total',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 0.1 JUL-1-2008', [])

            # Dump output into a file in yaml format
            stream = open(args[3] + '.yaml', 'w')
            stream.write(a.serialize_yaml())
            yaml.dump_all(b_list, stream)

            # Dump output into a file in XML file
            stream = open(args[3] + '.xml', 'w')
            stream.write(a.serialize_xml())
            for record in b_list:
                stream.writelines(xmlSerialize(record)[173:]. \
                    replace('\t', '    ').replace('\n</plist>', ''))
        else:
            exit()

    # Make and return a jurisdiction_slate
    def make_juris(self):
        b = self.random_elec()
        b['precinct_list'] = []
        
        # Make some precincts, currently with mostly hardcoded values
        b['number_of_precincts'] = 8
        for i in range(1,9):
            b['precinct_list'].append({})
            prec = b['precinct_list'][i - 1]
            prec['display_name'] = random.randint(1000,9999)
            prec['prec_id'] = 'PREC-' + str(i)
            prec['districts'] = []
            prec['voting places'] = []
            prec['voting places'].append({})
            prec['voting places'][0]['ballot_counters'] = random.randint(1,5)
            prec['voting places'][0]['ident'] = 'VLPC-' + str(i)
            prec['registered_voters'] = random.randint(900,1100)

        # Give the precincts some hardcoded districts
        l = b['precinct_list']
        n1 = 'City of Random'
        n2 = 'Random Creek Drainage District'
        n3 = 'State House District 11'
        n4 = 'State House District 12'
        l[0]['districts'].append({'display_name':n1, 'ident':'DIST-1'})
        l[0]['districts'].append({'display_name':n3, 'ident':'DIST-3'})
        l[1]['districts'].append({'display_name':n1, 'ident':'DIST-1'})
        l[1]['districts'].append({'display_name':n4, 'ident':'DIST-4'})
        l[2]['districts'].append({'display_name':n1, 'ident':'DIST-1'})
        l[2]['districts'].append({'display_name':n2, 'ident':'DIST-2'})
        l[2]['districts'].append({'display_name':n4, 'ident':'DIST-4'})
        l[3]['districts'].append({'display_name':n3, 'ident':'DIST-3'})
        l[4]['districts'].append({'display_name':n2, 'ident':'DIST-2'})
        l[4]['districts'].append({'display_name':n3, 'ident':'DIST-3'})
        l[5]['districts'].append({'display_name':n1, 'ident':'DIST-1'})
        l[5]['districts'].append({'display_name':n2, 'ident':'DIST-2'})
        l[5]['districts'].append({'display_name':n4, 'ident':'DIST-4'})
        l[6]['districts'].append({'display_name':n2, 'ident':'DIST-2'})
        l[7]['districts'].append({'display_name':n4, 'ident':'DIST-4'})        

        return b

    # Make and return a ballot with initialized data members
    def random_elec(self):
        b = {}
        self.cand_num = 1

        # Load a list of first and last names from file
        stream = open('first_names', 'r')
        self.fnames = stream.readlines()
        stream = open('last_names', 'r')
        self.lnames = stream.readlines()

        # Make the election headliner some random presidential election
        r = random.randint(0,3)
        b['election_name'] = str(r*4+2000) + " Presidential"
        b['number_of_precincts'] = 0
        b['vote_type'] = 'NULL'
        b['prec_id'] = 'NULL'
        
        # Generate a few contests
        b['contests'] = []
        for i in range(10):
            b['contests'].append(self.random_contest())            
        return b

    # Make and returns a contest object with initialized data members
    def random_contest(self):
        cont = {}

        # Generate a few candidates per contest
        cont['candidates'] = []
        r = random.randint(2,4)
        for i in range(0,r):            
            cont['candidates'].append(self.random_candidate(False))
        cont['candidates'].append(self.random_candidate(True))

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
                        cont['contest_id'] = 'Rep1stDistrict'
                    elif r == 2:
                        cont['contest_id'] = 'Rep2ndDistrict'
                    elif r == 3:
                        cont['contest_id'] = 'Rep3rdDistrict'
                    else:
                        cont['contest_id'] = 'Rep'+str(r)+'thDistrict'
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
                        cont['contest_id'] = 'StateRep1stHouse'
                    elif r == 2:
                        cont['contest_id'] = 'StateRep2ndHouse'
                    elif r == 3:
                        cont['contest_id'] = 'StateRep3rdHouse'
                    else:
                        cont['contest_id'] = 'StateRep'+str(r)+'thHouse'
                    break
        else:
            cont['display_name'] = 'Supreme Court Justice'
            cont['contest_id'] = 'JustSupCrt'
            self.already_used_supreme = True
    
        # Generate a space for blank and over votes for this contest,
        #  and also for total votes
        cont['uncounted_ballots'] = {}
        cont['uncounted_ballots']['blank_votes'] = 0
        cont['uncounted_ballots']['over_votes'] = 0
        cont['total_votes'] = 0

        cont['district_id'] = 'DIST-' + str(random.randint(1,4))
        cont['voting_method_id'] = 'VOTM-' + str(random.randint(1,5))
        return cont

    # Make and returns a candidate object with initialized data members
    def random_candidate(self, write_in):
        cand = {}
        
        # Count just gets a null value, since it is irrelevant to the
        #  specs generated here.
        cand['count'] = 0
        
        # If the "candidate" to be generated is just a placeholder for
        #  write-in candidates, then use some hardcoded field values
        if write_in:
            cand['display_name'] = "Write-In Votes"
            cand['ident'] = 'CAND-000'
            cand['party_id'] = 'PART-0'
        else:
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

def printUsage():
    print "Usage: test_data_generator.py jurisdiction [OUTPUT ELECTION FILE]"
    print "   OR: test_data_generator.py contestlist [OUTPUT ELECTION FILE]"
    print "   OR: test_data_generator.py counts [#  OF SAMPLES]",
    print "[INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]"
    exit()

def main(): 
    # First make sure that the command line input is valid. If it is not
    #  then output a usage statement and exit    
    if len(sys.argv) == 1: sys.argv.append("")
    type = sys.argv[1]
    if type == "jurisdiction":
        if len(sys.argv) != 3:
            printUsage()
    elif type == "contestlist":
        if len(sys.argv) != 3:
            printUsage()
    elif type == "counts":
        if len(sys.argv) != 5:
            printUsage()
    else:
        printUsage()
    # Get rid of unneccesary command line arguments and generate random
    #  data of the specified type
    args = sys.argv[1:]
    p = ProvideRandomBallots(args)

    if type == "jurisdiction":
        print "Done. Generated sample jurisdiction template files",
        print sys.argv[2] + ".yaml and " + sys.argv[2] + ".xml \n"
    elif type == "contestlist":
        print "Done. Generated sample contestlist template files",
        print sys.argv[2] + ".yaml and " + sys.argv[2] + ".xml \n"
    else:
        print "Done. Generated sample ballot files",
        print sys.argv[4] + ".yaml and " + sys.argv[4] + ".xml \n"

    return 0
    
if __name__ == '__main__': main()
