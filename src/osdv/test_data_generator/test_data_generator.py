#!/usr/bin/env python

"""
Developed with Python 2.6.2
Name: test_data_generator.py
Author: Mike Anderson
Created: Jul 30, 2009
Purpose: To generate test data files for the merger and tabulator
"""

from __future__ import with_statement
import random
import yaml
import sys
import copy
import uuid
from plistlib import writePlistToString as xmlSerialize

import audit_header

class ProvideRandomBallots(object):

    """
    Provide random election specs or random ballot counts
    """

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
            b['jurisdiction_display_name'] = \
             args[1][args[1].rfind('/') + 1:len(args[1])].encode("ascii")
        
            # Dump output into a file in yaml format
            with open(''.join([args[1],'.yaml']), 'w') as stream:
                stream.write(a.serialize_yaml())
                yaml.dump(b, stream)
            
            # Dump output into a file in XML file
            with open(''.join([args[1],'.xml']), 'w') as stream:
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
            with open(''.join([args[1],'.yaml']), 'w') as stream:
                stream.write(a.serialize_yaml())
                yaml.dump(b, stream)

            # Dump output into a file in XML file
            with open(''.join([args[1], '.xml']), 'w') as stream:
                stream.write(a.serialize_xml())
                stream.writelines(xmlSerialize(b)[173:]. \
                    replace('\t', '    ').replace('\n</plist>', ''))

        elif self.type == 'counts':
            # Extract and apply flags if there are any
            if len(args) == 5:
                if args[4] == '-1':
                    r_min = 1
                    r_max = 1
                elif args[4][0] == '+':
                    r_min = 0
                    r_max = int(args[4][1:])
                args.remove(args[4])
            else:
                r_min = 0
                r_max = 99

            # Load election specs from given file in yaml format
            with open(''.join([args[2],'.yaml']), 'r') as stream:
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
                    if key not in ['contest_list', 'precinct_list',
                     'jurisdiction_display_name']:
                        b[key] = e[key]
                b['contest_list'] = []
                b['type'] = 'ballot_counter_total'
                prec_num = random.randint(1,8)
                b['prec_id'] = ''.join(['PREC-',str(prec_num)])
                if e.has_key('precinct_list'):
                    b['registered_voters'] = \
                     e['precinct_list'][prec_num-1]['registered_voters']
                for j in range(len(e['contest_list'])):
                    # If the template was a jurisdiction_slate, then
                    #  do not include contests that were not generated
                    #  in a district in this precinct.
                    if e.has_key('precinct_list'):
                        valid_contest = False
                        for prec in e['precinct_list']:
                            if prec['prec_id'] == b['prec_id']:
                                for dist in prec['districts']:
                                    if dist['ident'] == \
                                     e['contest_list'][j]['district_id']:
                                        valid_contest = True
                                        break
                        if not valid_contest:
                            continue
                    b['contest_list'].append(copy.deepcopy(e['contest_list'][j]))
                    cont = b['contest_list'][-1]
                    if not cont.has_key('total_votes'):
                        cont['total_votes'] = 0
                        cont['uncounted_ballots'] = {}
                        cont['uncounted_ballots']['blank_votes'] = 0
                        cont['uncounted_ballots']['over_votes'] = 0
                        cont['voting_method_id'] = ''.join(['VOTM-',
                         str(random.randint(1,5))])
                    for cand in cont['candidates']:
                        if cand['display_name'] == 'Write-In Votes':
                            cand['count'] = random.randint(r_min, r_max)
                        else:
                            cand['count'] = random.randint(r_min, r_max)
                        cont['total_votes'] += cand['count']
                    cont['uncounted_ballots']['blank_votes'] = \
                     random.randint(r_min,r_max)
                    cont['uncounted_ballots']['over_votes'] = \
                     random.randint(r_min,r_max)

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
            with open(''.join([args[3],'.yaml']), 'w') as stream:
                stream.write(a.serialize_yaml())
                yaml.dump_all(b_list, stream)

            # Dump output into a file in XML file
            with open(''.join([args[3],'.xml']), 'w') as stream:
                stream.write(a.serialize_xml())
                for record in b_list:
                    stream.writelines(xmlSerialize(record)[173:]. \
                        replace('\t', '    ').replace('\n</plist>', ''))
        else:
            raise StandardError('Incorrect data generation type')

    def make_juris(self):
        """
        Make and return a jurisdiction_slate
        """

        b = self.random_elec()
        b['precinct_list'] = []
        
        # Make some precincts, currently with mostly hardcoded values
        b['number_of_precincts'] = 8
        for i in range(1,9):
            b['precinct_list'].append({})
            prec = b['precinct_list'][i - 1]
            prec['display_name'] = random.randint(1000,9999)
            prec['prec_id'] = ''.join(['PREC-',str(i)])
            prec['districts'] = []
            prec['voting places'] = []
            prec['voting places'].append({})
            prec['voting places'][0]['ballot_counters'] = random.randint(1,5)
            prec['voting places'][0]['ident'] = ''.join(['VLPC-',str(i)])
            prec['registered_voters'] = random.randint(900,1100)
            b['registered_voters'] += prec['registered_voters']

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

    def random_elec(self):
        """
        Make and return a ballot with initialized data members
        """

        b = {}
        self.cand_num = 1

        # Load a list of first and last names from file
        with open('first_names', 'r') as stream:
            self.fnames = stream.readlines()
        with open('last_names', 'r') as stream:
            self.lnames = stream.readlines()

        # Make the election headliner some random presidential election
        r = random.randint(0,3)
        b['display_name'] = ''.join([str(r*4+2000),' Presidential'])
        b['number_of_precincts'] = 0
        b['vote_type'] = 'NULL'
        b['prec_id'] = 'NULL'
        b['registered_voters'] = 0
        
        # Generate a few contests
        b['contest_list'] = []
        for i in range(10):
            b['contest_list'].append(self.random_contest())            
        return b

    def random_contest(self):
        """
        Make and return a contest object with initialized data members
        """

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
                        cont['contest_id'] = ''.join(['Rep',str(r),
                         'thDistrict'])
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
                        cont['contest_id'] = ''.join(['StateRep',str(r),
                         'thHouse'])
                    break
        else:
            cont['display_name'] = 'Supreme Court Justice'
            cont['contest_id'] = 'JustSupCrt'
            self.already_used_supreme = True
    
        cont['district_id'] = ''.join(['DIST-',str(random.randint(1,4))])
        return cont

    def random_candidate(self, write_in):
        """
        Make and return a candidate object with initialized data
         members
        """
        
        cand = {}
        
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
                    cand['ident'] = ''.join(['CAND-',str(r)])
                    break
            cand['party_id'] = ''.join(['PART-',str(random.randint(1,9))])
        
        return cand

    def random_fullname(self):
        """
        Make and return a random full name string
        """
        
        # Generate a first and last name combination
        fname = self.fnames[random.randint(0, len(self.fnames) - 1)].strip()
        lname = self.lnames[random.randint(0, len(self.lnames) - 1)].strip()
        fullname = ' '.join([fname,lname])
        
        if self.already_used_names.count(fullname) == 0:
            self.already_used_names.append(fullname)
            return fullname
        else:
            return(self.random_fullname())      

def printUsage():
    print 'Usage: test_data_generator.py jurisdiction [OUTPUT ELECTION FILE]'
    print '   OR: test_data_generator.py contestlist [OUTPUT ELECTION FILE]'
    print '   OR: test_data_generator.py counts [#  OF SAMPLES]'
    print '       [INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]'
    print '   OR: test_data_generator.py counts [OPTION] [#  OF SAMPLES]'
    print '       [INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]'
    print
    print
    print 'Where [OPTION] can consist of one of the following:'
    print '   -1'
    print '      All count fields in the generated BCT output will contain'
    print '      the value 1'
    print 
    print '   +[NUMBER]'
    print '      All count fields in the generated BCT output will contain'
    print '      a value between 0 and [NUMBER]'
    exit()

def main(): 
    # First make sure that the command line input is valid. If it is not
    #  then output a usage statement and exit
    if len(sys.argv) == 1: sys.argv.append('')
    type = sys.argv[1]
    if type == 'jurisdiction':
        if len(sys.argv) != 3:
            printUsage()
    elif type == 'contestlist':
        if len(sys.argv) != 3:
            printUsage()
    elif type == 'counts':
        # This condition is complicated by the possibility of BCT flags
        if len(sys.argv) != 5 and \
         ( len(sys.argv) != 6 or (not sys.argv[5][0] in ['-','+']) ):
            printUsage()
    else:
        printUsage()
    # Get rid of unneccesary command line arguments and generate random
    #  data of the specified type
    p = ProvideRandomBallots(sys.argv[1:])

    if type == 'jurisdiction':
        print 'Done. Generated sample jurisdiction template files',
        print '%s.yaml and %s.xml\n' % (sys.argv[2], sys.argv[2])

    elif type == 'contestlist':
        print 'Done. Generated sample contestlist template files',
        print '%s.yaml and %s.xml\n' % (sys.argv[2], sys.argv[2])
    else:
        print 'Done. Generated sample ballot files',
        print '%s.yaml and %s.xml\n' % (sys.argv[4], sys.argv[4])

    return 0
    
if __name__ == '__main__': main()
